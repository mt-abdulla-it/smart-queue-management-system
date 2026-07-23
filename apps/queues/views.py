"""
Queues Views.
Handles queue booking, status checking, and staff queue management.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, TemplateView
from apps.core.mixins import RoleRequiredMixin
from apps.branches.models import Department, Service

from .models import QueueToken, QueueHistory
from .forms import QueueBookingForm
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
            'hold': 'HOLD'
        }
        
        new_status = status_map.get(action)
        if new_status and new_status != old_status:
            token.status = new_status
            token.save()
            
            action_mapping = {
                'SERVING': QueueHistory.Action.SERVING,
                'SKIPPED': QueueHistory.Action.SKIPPED,
                'COMPLETED': QueueHistory.Action.COMPLETED,
                'HOLD': QueueHistory.Action.ON_HOLD,
            }
            history_action = action_mapping.get(new_status, QueueHistory.Action.CREATED)
            
            QueueHistory.objects.create(
                token=token,
                action_by=request.user,
                action=history_action,
                notes=f"Status changed to {new_status} via staff panel."
            )
            
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

