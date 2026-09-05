"""
Queues Views.
Handles queue booking, status checking, and staff queue management.
"""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, TemplateView
from apps.core.mixins import RoleRequiredMixin, StaffRequiredMixin
from apps.branches.models import Department, Service

from .models import QueueToken, QueueHistory
from .forms import QueueBookingForm, TransferTicketForm
from .utils import generate_qr_code, generate_pdf_token


# ---------- USER VIEWS ---------- #

class BookQueueView(LoginRequiredMixin, CreateView):
    """View for users to book a new queue token."""
    model = QueueToken
    form_class = QueueBookingForm
    template_name = 'queues/book.html'

    def get_success_url(self):
        return reverse('queues:token_detail', kwargs={'pk': self.object.pk})

    @transaction.atomic
    def form_valid(self, form):
        service = form.cleaned_data['service']
        
        # Calculate the next token number for the day
        today = timezone.now().date()
        last_token = QueueToken.objects.filter(
            service=service,
            created_at__date=today
        ).order_by('-id').first()
        
        if last_token:
            # Extract number from format PREFIX-001
            try:
                last_num = int(last_token.token_number.split('-')[-1])
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1
            
        token_number = f"{service.prefix}-{next_num:03d}"
        
        # Save the token
        token = form.save(commit=False)
        token.user = self.request.user
        token.token_number = token_number
        token.status = 'WAITING'
        token.queue_date = today
        token.save()
        
        # Generate QR Code storing the token detail URL
        # We need the full absolute URI for the QR code
        qr_url = self.request.build_absolute_uri(reverse('queues:token_detail', kwargs={'pk': token.pk}))
        qr_file = generate_qr_code(qr_url)
        token.qr_code.save(f"token_{token.id}_qr.png", qr_file, save=True)

        # Log History
        QueueHistory.objects.create(
            token=token,
            action_by=self.request.user,
            action=QueueHistory.Action.CREATED,
            notes="Token generated online."
        )

        messages.success(self.request, f"Queue booked successfully! Your token is {token_number}")
        self.object = token
        return super().form_valid(form)


class MyTokensListView(LoginRequiredMixin, ListView):
    """View for a user to see their active and past tokens."""
    model = QueueToken
    template_name = 'queues/my_tokens.html'
    context_object_name = 'tokens'

    def get_queryset(self):
        return QueueToken.objects.filter(user=self.request.user).order_by('-created_at')


class TokenDetailView(LoginRequiredMixin, DetailView):
    """View to see details of a specific token and its live status."""
    model = QueueToken
    template_name = 'queues/token_detail.html'
    context_object_name = 'token'

    def get_queryset(self):
        # Users can only see their own tokens, staff/admin can see any
        qs = QueueToken.objects.all()
        if self.request.user.role == 'USER':
            qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.get_object()
        
        # Calculate current position in line
        if token.status == 'WAITING':
            position = QueueToken.objects.filter(
                service=token.service,
                status='WAITING',
                created_at__lt=token.created_at
            ).count() + 1
            context['position'] = position
            context['estimated_wait'] = position * (getattr(token.service, 'avg_service_time_minutes', 10))
        
        return context


class DownloadTokenPDFView(LoginRequiredMixin, View):
    """Download the token as a PDF."""
    def get(self, request, pk):
        qs = QueueToken.objects.all()
        if request.user.role == 'USER':
            qs = qs.filter(user=request.user)
        
        token = get_object_or_404(qs, pk=pk)
        pdf_buffer = generate_pdf_token(token)
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="token_{token.token_number}.pdf"'
        return response


# ---------- AJAX VIEWS ---------- #

def load_departments(request):
    """AJAX view to load departments for a branch."""
    branch_id = request.GET.get('branch')
    departments = Department.objects.filter(branch_id=branch_id, is_active=True).values('id', 'name')
    return JsonResponse(list(departments), safe=False)

def load_services(request):
    """AJAX view to load services for a department."""
    department_id = request.GET.get('department')
    services = Service.objects.filter(department_id=department_id, is_active=True).values('id', 'name')
    return JsonResponse(list(services), safe=False)


# ---------- STAFF VIEWS ---------- #

class StaffManageQueueView(RoleRequiredMixin, TemplateView):
    """Staff dashboard for managing the queue."""
    template_name = 'dashboard/staff_manage.html'
    allowed_roles = ['STAFF', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        
        qs = QueueToken.objects.filter(created_at__date=today)
        if hasattr(self.request.user, 'staff_profile') and self.request.user.staff_profile.department:
            qs = qs.filter(service__department=self.request.user.staff_profile.department)
        
        context['waiting_tokens'] = qs.filter(status='WAITING').order_by('created_at')
        context['serving_tokens'] = qs.filter(status='SERVING').order_by('-updated_at')
        context['services'] = Service.objects.filter(is_active=True)
        
        return context


class ChangeTokenStatusView(RoleRequiredMixin, View):
    """Handle status changes by staff (Call, Skip, Complete)."""
    allowed_roles = ['STAFF', 'ADMIN']
    
    @transaction.atomic
    def post(self, request, pk, action):
        token = get_object_or_404(QueueToken, pk=pk)
        old_status = token.status
        
        status_map = {
            'call': 'SERVING',
            'skip': 'SKIPPED',
            'complete': 'COMPLETED',
            'hold': 'ON_HOLD'
        }
        
        new_status = status_map.get(action)
        if new_status and new_status != old_status:
            token.status = new_status
            
            # Record counter number and staff member calling token
            counter_from_post = request.POST.get('counter_number', '').strip()
            if counter_from_post:
                token.counter_number = counter_from_post
            elif hasattr(request.user, 'staff_profile') and getattr(request.user.staff_profile, 'counter_number', None):
                token.counter_number = request.user.staff_profile.counter_number
                
            token.called_by = request.user
            if new_status == 'SERVING':
                token.called_at = timezone.now()
                token.serving_at = timezone.now()
            elif new_status == 'COMPLETED':
                token.completed_at = timezone.now()
                
            token.save()
            
            action_mapping = {
                'SERVING': QueueHistory.Action.CALLED if action == 'call' else QueueHistory.Action.SERVING,
                'SKIPPED': QueueHistory.Action.SKIPPED,
                'COMPLETED': QueueHistory.Action.COMPLETED,
                'ON_HOLD': QueueHistory.Action.ON_HOLD,
            }
            history_action = action_mapping.get(new_status, QueueHistory.Action.CREATED)
            
            QueueHistory.objects.create(
                token=token,
                action_by=request.user,
                action=history_action,
                notes=f"Token {token.token_number} status set to {new_status} at {token.counter_number}."
            )
            
        return redirect('queues:staff_manage')


class TransferTokenView(RoleRequiredMixin, View):
    """Handle ticket transfer to a new service by staff/admin."""
    allowed_roles = ['STAFF', 'ADMIN']

    @transaction.atomic
    def post(self, request, pk):
        token = get_object_or_404(QueueToken, pk=pk)
        service_id = request.POST.get('target_service')
        transfer_notes = request.POST.get('notes', '').strip()
        
        if not service_id:
            messages.error(request, "Please select a valid destination service.")
            return redirect('queues:staff_manage')
            
        target_service = get_object_or_404(Service, pk=service_id, is_active=True)
        old_service_name = token.service.name
        
        # Update service and reset status to WAITING
        token.service = target_service
        token.branch = target_service.department.branch
        token.status = 'WAITING'
        token.called_by = None
        token.save()
        
        note_text = f"Transferred from '{old_service_name}' to '{target_service.name}'."
        if transfer_notes:
            note_text += f" Note: {transfer_notes}"
            
        QueueHistory.objects.create(
            token=token,
            action_by=request.user,
            action=QueueHistory.Action.TRANSFERRED,
            notes=note_text
        )
        
        messages.success(request, f"Token {token.token_number} successfully transferred to {target_service.name}.")
        return redirect('queues:staff_manage')


class QueueHistoryListView(RoleRequiredMixin, ListView):
    """View to see history of all tokens (for STAFF/ADMIN)."""
    model = QueueToken
    template_name = 'queues/my_tokens.html'
    context_object_name = 'tokens'
    allowed_roles = ['STAFF', 'ADMIN']

    def get_queryset(self):
        return QueueToken.objects.all().order_by('-created_at')

class AdminQueueListView(RoleRequiredMixin, ListView):
    """View to see all tokens across all branches (ADMIN only)."""
    model = QueueToken
    template_name = 'queues/my_tokens.html'
    context_object_name = 'tokens'
    allowed_roles = ['ADMIN']

    def get_queryset(self):
        return QueueToken.objects.all().order_by('-created_at')

class LiveDisplayView(TemplateView):
    """Public view for the live queue display screen."""
    template_name = 'queues/live_display.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        context['serving_tokens'] = QueueToken.objects.filter(
            status='SERVING', created_at__date=today
        ).order_by('-updated_at')[:5]
        
        context['waiting_tokens'] = QueueToken.objects.filter(
            status='WAITING', created_at__date=today
        ).order_by('created_at')[:10]
        
        return context

class LiveWaitingListAPIView(View):
    """API endpoint to return the current waiting list for the live display."""
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        waiting_tokens = QueueToken.objects.filter(
            status='WAITING', created_at__date=today
        ).order_by('created_at')[:10]
        
        data = [
            {
                'token_number': t.token_number,
                'service': t.service.name
            } for t in waiting_tokens
        ]
        return JsonResponse(data, safe=False)


class TokenLiveStatusAPIView(View):
    """API endpoint returning live status, position, wait time, and progress for a specific token."""
    def get(self, request, pk, *args, **kwargs):
        qs = QueueToken.objects.all()
        if request.user.is_authenticated and getattr(request.user, 'role', None) == 'USER':
            qs = qs.filter(user=request.user)
        
        token = get_object_or_404(qs, pk=pk)
        
        position = 0
        total_ahead = 0
        estimated_wait = 0
        progress_percent = 100
        
        avg_time = getattr(token.service, 'avg_service_time_minutes', 10)
        
        if token.status == 'WAITING':
            # Count tokens ahead in WAITING status created before this token
            waiting_ids = list(QueueToken.objects.filter(
                service=token.service,
                status='WAITING',
                created_at__date=token.created_at.date()
            ).order_by('created_at').values_list('id', flat=True))
            
            try:
                position = waiting_ids.index(token.id) + 1
            except ValueError:
                position = 1
                
            total_ahead = position - 1
            estimated_wait = position * avg_time
            
            # Calculate total issued tokens for this service today up to this token
            total_issued = QueueToken.objects.filter(
                service=token.service,
                created_at__date=token.created_at.date(),
                created_at__lte=token.created_at
            ).count()
            
            processed_before = QueueToken.objects.filter(
                service=token.service,
                created_at__date=token.created_at.date(),
                created_at__lt=token.created_at,
                status__in=['SERVING', 'COMPLETED', 'SKIPPED']
            ).count()
            
            if total_issued > 0:
                calc_progress = int(15 + (processed_before / float(total_issued)) * 75)
                progress_percent = min(max(calc_progress, 15), 90)
            else:
                progress_percent = 20
        elif token.status == 'SERVING':
            progress_percent = 95
            position = 0
            total_ahead = 0
            estimated_wait = 0
        elif token.status == 'COMPLETED':
            progress_percent = 100
            position = 0
            total_ahead = 0
            estimated_wait = 0
        else:
            progress_percent = 50
        
        currently_serving = QueueToken.objects.filter(
            service=token.service,
            created_at__date=token.created_at.date(),
            status='SERVING'
        ).order_by('-updated_at').first()
        
        return JsonResponse({
            'id': token.id,
            'token_number': token.token_number,
            'status': token.status,
            'status_display': token.get_status_display() if hasattr(token, 'get_status_display') else token.status,
            'position': position,
            'total_ahead': total_ahead,
            'estimated_wait': estimated_wait,
            'progress_percent': progress_percent,
            'currently_serving': currently_serving.token_number if currently_serving else None,
            'service_name': token.service.name,
            'updated_at': token.updated_at.strftime('%H:%M:%S') if token.updated_at else None
        })


class KioskView(TemplateView):
    """Interactive Touchscreen Self-Service Kiosk View."""
    template_name = 'queues/kiosk.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        departments = Department.objects.filter(is_active=True).prefetch_related('services')
        services_data = []
        
        for dept in departments:
            for service in dept.services.filter(is_active=True):
                waiting_count = QueueToken.objects.filter(
                    service=service,
                    created_at__date=today,
                    status='WAITING'
                ).count()
                
                est_wait = waiting_count * getattr(service, 'avg_service_time_minutes', 10)
                
                services_data.append({
                    'id': service.id,
                    'name': service.name,
                    'prefix': service.prefix,
                    'department_name': dept.name,
                    'icon': service.icon if hasattr(service, 'icon') else 'bi-ticket-perforated',
                    'description': service.description,
                    'waiting_count': waiting_count,
                    'est_wait': est_wait,
                })
                
        context['services_list'] = services_data
        return context


class KioskCreateTokenAPIView(View):
    """AJAX Endpoint to issue a new queue token from the interactive Kiosk."""
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        import json
        try:
            data = json.loads(request.body) if request.body else request.POST
            service_id = data.get('service_id')
            is_priority = data.get('is_priority', False)
            
            if not service_id:
                return JsonResponse({'success': False, 'error': 'Service ID is required'}, status=400)
                
            service = get_object_or_404(Service, id=service_id)
            today = timezone.now().date()
            
            # Determine or create user for kiosk ticket
            if request.user.is_authenticated:
                user = request.user
            else:
                User = get_user_model()
                user, _ = User.objects.get_or_create(
                    email='kiosk@sqms.local',
                    defaults={
                        'first_name': 'Kiosk',
                        'last_name': 'Walk-in',
                        'role': 'USER'
                    }
                )
            
            # Next token number for today
            last_token = QueueToken.objects.filter(
                service=service,
                created_at__date=today
            ).order_by('-id').first()
            
            if last_token:
                try:
                    last_num = int(last_token.token_number.split('-')[-1])
                    next_num = last_num + 1
                except ValueError:
                    next_num = 1
            else:
                next_num = 1
                
            token_number = f"{service.prefix}-{next_num:03d}"
            
            branch = service.department.branch if (service.department and hasattr(service.department, 'branch')) else None
            if not branch:
                from apps.branches.models import Branch
                branch = Branch.objects.filter(is_active=True).first()

            # Save token
            token = QueueToken.objects.create(
                user=user,
                service=service,
                branch=branch,
                token_number=token_number,
                status=QueueToken.Status.WAITING,
                queue_date=today,
                booking_type=QueueToken.BookingType.KIOSK,
                is_priority=is_priority
            )
            
            # QR code generation
            qr_url = request.build_absolute_uri(reverse('queues:token_detail', kwargs={'pk': token.pk}))
            qr_file = generate_qr_code(qr_url)
            token.qr_code.save(f"token_{token.id}_qr.png", qr_file, save=True)
            
            # Log history
            QueueHistory.objects.create(
                token=token,
                action_by=user,
                action=QueueHistory.Action.CREATED,
                notes="Token generated via Self-Service Kiosk."
            )
            
            # Calculate current waiting position
            waiting_ids = list(QueueToken.objects.filter(
                service=service,
                status='WAITING',
                created_at__date=today
            ).order_by('created_at').values_list('id', flat=True))
            
            try:
                position = waiting_ids.index(token.id) + 1
            except ValueError:
                position = 1
                
            avg_time = getattr(service, 'avg_service_time_minutes', 10)
            estimated_wait = position * avg_time
            
            return JsonResponse({
                'success': True,
                'token_id': token.id,
                'token_number': token.token_number,
                'service_name': service.name,
                'department_name': service.department.name if service.department else 'General',
                'branch_name': service.department.branch.name if service.department and service.department.branch else 'Main Hospital',
                'qr_code_url': token.qr_code.url if token.qr_code else '',
                'token_detail_url': reverse('queues:token_detail', kwargs={'pk': token.pk}),
                'position': position,
                'estimated_wait': estimated_wait,
                'created_at': timezone.localtime(token.created_at).strftime('%I:%M %p, %b %d, %Y'),
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class TokenArrivalCheckinAPIView(View):
    """AJAX endpoint for patient to confirm physical arrival at venue."""
    def post(self, request, pk, *args, **kwargs):
        token = get_object_or_404(QueueToken, pk=pk)
        token.notes = (token.notes + " | Patient checked in on-site.").strip(" |")
        token.save()
        
        QueueHistory.objects.create(
            token=token,
            action_by=request.user if request.user.is_authenticated else token.user,
            action=QueueHistory.Action.CALLED if token.status == 'CALLED' else QueueHistory.Action.CREATED,
            notes="Patient confirmed arrival on mobile."
        )
        return JsonResponse({'success': True, 'message': 'Arrival checked in successfully!'})


# ---------- QR SCANNER & TOKEN VERIFICATION VIEWS ---------- #

class StaffTokenScannerView(StaffRequiredMixin, TemplateView):
    """View for staff and admin users to scan and verify customer token QR codes."""
    template_name = 'queues/scanner.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context['title'] = 'Digital QR Code Token Scanner'
        context['today_date'] = today.strftime('%B %d, %Y')
        context['today_scans_count'] = QueueHistory.objects.filter(
            created_at__date=today,
            action__in=[QueueHistory.Action.CALLED, QueueHistory.Action.SERVING, QueueHistory.Action.COMPLETED]
        ).count()
        return context


class TokenVerificationAPIView(View):
    """
    API endpoint for verifying scanned QR codes or manually entered token numbers.
    Supports performing immediate lifecycle actions (checkin, call, serve, complete, hold).
    """

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def _resolve_token(self, query):
        """Resolves target QueueToken from raw query string, URL, token number, or verification code."""
        if not query:
            return None
            
        query = str(query).strip()

        # Handle full URL scanning e.g. .../queues/token/42/ or .../queues/verify/42/
        if '/queues/token/' in query or '/queues/verify/' in query:
            import re
            match = re.search(r'/(?:token|verify)/(\d+)/?', query)
            if match:
                token_id = int(match.group(1))
                token = QueueToken.objects.filter(pk=token_id).first()
                if token:
                    return token

        # Numeric query lookup by ID
        if query.isdigit():
            token = QueueToken.objects.filter(pk=int(query)).first()
            if token:
                return token

        # Search by token_number or verification_code for today or recent
        today = timezone.now().date()
        token = QueueToken.objects.filter(
            models.Q(token_number__iexact=query) | models.Q(verification_code__iexact=query)
        ).order_by('-created_at').first()

        if token:
            return token

        # Fallback search by partial token_number
        return QueueToken.objects.filter(
            token_number__icontains=query
        ).order_by('-created_at').first()

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query') or request.GET.get('token_query') or request.GET.get('token_number')
        return self._handle_verification(request, query)

    def post(self, request, *args, **kwargs):
        import json
        query = request.POST.get('query') or request.POST.get('token_query') or request.POST.get('token_number')
        
        # Check JSON body if POST form-data is empty
        if not query and request.body:
            try:
                data = json.loads(request.body)
                query = data.get('query') or data.get('token_query') or data.get('token_number')
                action = data.get('action')
            except Exception:
                action = None
        else:
            action = request.POST.get('action')

        return self._handle_verification(request, query, action)

    def _handle_verification(self, request, query, action=None):
        if not query:
            return JsonResponse({'success': False, 'error': 'No token query or QR payload provided.'}, status=400)

        token = self._resolve_token(query)
        if not token:
            return JsonResponse({
                'success': False,
                'error': f'Token matching "{query}" was not found.'
            }, status=404)

        today = timezone.now().date()
        is_valid_today = (token.queue_date == today)

        # Execute requested action if provided
        action_message = None
        if action:
            action = action.lower()
            now = timezone.now()
            user = request.user if request.user.is_authenticated else None

            if action == 'checkin':
                if "On-site arrival confirmed" not in token.notes:
                    token.notes = f"{token.notes} | On-site arrival confirmed via QR Scanner.".strip(" |")
                    token.save()
                    QueueHistory.objects.create(
                        token=token,
                        action_by=user,
                        action=QueueHistory.Action.CREATED,
                        notes="Arrival confirmed via Staff QR Scanner."
                    )
                action_message = f"Token {token.token_number} arrival checked in!"

            elif action == 'call':
                token.status = QueueToken.Status.CALLED
                token.called_at = now
                if user:
                    token.called_by = user
                token.save()
                QueueHistory.objects.create(
                    token=token,
                    action_by=user,
                    action=QueueHistory.Action.CALLED,
                    notes="Called via Staff QR Scanner."
                )
                action_message = f"Token {token.token_number} called!"

            elif action == 'serve':
                token.status = QueueToken.Status.SERVING
                token.serving_at = now
                token.save()
                QueueHistory.objects.create(
                    token=token,
                    action_by=user,
                    action=QueueHistory.Action.SERVING,
                    notes="Serving started via Staff QR Scanner."
                )
                action_message = f"Token {token.token_number} is now SERVING!"

            elif action == 'complete':
                token.status = QueueToken.Status.COMPLETED
                token.completed_at = now
                token.save()
                QueueHistory.objects.create(
                    token=token,
                    action_by=user,
                    action=QueueHistory.Action.COMPLETED,
                    notes="Completed service via Staff QR Scanner."
                )
                action_message = f"Token {token.token_number} marked COMPLETED!"

            elif action == 'hold':
                token.status = QueueToken.Status.ON_HOLD
                token.save()
                QueueHistory.objects.create(
                    token=token,
                    action_by=user,
                    action=QueueHistory.Action.ON_HOLD,
                    notes="Placed on hold via Staff QR Scanner."
                )
                action_message = f"Token {token.token_number} placed ON HOLD."

            elif action == 'cancel':
                token.status = QueueToken.Status.CANCELLED
                token.save()
                QueueHistory.objects.create(
                    token=token,
                    action_by=user,
                    action=QueueHistory.Action.CANCELLED,
                    notes="Cancelled via Staff QR Scanner."
                )
                action_message = f"Token {token.token_number} CANCELLED."

        # Calculate current waiting position if WAITING
        position = token.position
        if token.status == QueueToken.Status.WAITING:
            waiting_ids = list(QueueToken.objects.filter(
                service=token.service,
                status=QueueToken.Status.WAITING,
                queue_date=token.queue_date
            ).order_by('created_at').values_list('id', flat=True))
            try:
                position = waiting_ids.index(token.id) + 1
            except ValueError:
                position = 1

        customer_name = token.user.get_full_name() or token.user.username if token.user else 'Guest Customer'

        return JsonResponse({
            'success': True,
            'message': action_message or 'Token QR verified successfully.',
            'is_valid_today': is_valid_today,
            'token': {
                'id': token.id,
                'token_number': token.token_number,
                'customer_name': customer_name,
                'customer_email': token.user.email if token.user else '',
                'service_name': token.service.name,
                'department_name': token.service.department.name if token.service.department else 'General',
                'branch_name': token.branch.name if token.branch else 'Main Branch',
                'status': token.status,
                'status_display': token.get_status_display(),
                'booking_type': token.get_booking_type_display(),
                'triage_level': token.get_triage_level_display(),
                'is_priority': token.is_priority,
                'counter_number': token.counter_number or 'Counter 1',
                'position': position,
                'estimated_wait_minutes': token.estimated_wait_minutes,
                'verification_code': token.verification_code or '',
                'queue_date': str(token.queue_date),
                'booked_at': timezone.localtime(token.booked_at).strftime('%I:%M %p, %b %d, %Y') if token.booked_at else '',
                'notes': token.notes or '',
                'detail_url': reverse('queues:token_detail', kwargs={'pk': token.pk}),
                'verify_url': reverse('queues:verify_token', kwargs={'pk': token.pk}),
                'qr_code_url': token.qr_code.url if token.qr_code else '',
            }
        })


class TokenVerificationDetailView(LoginRequiredMixin, DetailView):
    """Standalone page displaying token verification badge and details."""
    model = QueueToken
    template_name = 'queues/verify_detail.html'
    context_object_name = 'token'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.object
        today = timezone.now().date()
        context['is_valid_today'] = (token.queue_date == today)
        status_classes = {
            'WAITING': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
            'CALLED': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
            'SERVING': 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
            'COMPLETED': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
            'CANCELLED': 'bg-rose-500/20 text-rose-400 border-rose-500/30',
            'NO_SHOW': 'bg-slate-500/20 text-slate-400 border-slate-500/30',
            'ON_HOLD': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
            'SKIPPED': 'bg-slate-500/20 text-slate-400 border-slate-500/30',
        }
        context['status_class'] = status_classes.get(token.status, 'bg-slate-500/20 text-slate-400')
        return context



