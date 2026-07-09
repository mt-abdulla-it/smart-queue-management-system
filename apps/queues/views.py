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
            
        token_number = f"{service.token_prefix}-{next_num:03d}"
        
        # Save the token
        token = form.save(commit=False)
        token.user = self.request.user
        token.token_number = token_number
        token.status = 'WAITING'
        token.save()
        
        # Generate QR Code storing the token detail URL
        # We need the full absolute URI for the QR code
        qr_url = self.request.build_absolute_uri(reverse('queues:token_detail', kwargs={'pk': token.pk}))
        qr_file = generate_qr_code(qr_url)
        token.qr_code.save(f"token_{token.id}_qr.png", qr_file, save=True)

        # Log History
        QueueHistory.objects.create(
            token=token,
            changed_by=self.request.user,
            from_status='',
            to_status='WAITING',
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
            context['estimated_wait'] = position * token.service.estimated_time_mins
        
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
        
        # In a real app, we'd filter by the staff member's assigned service.
        # For Phase 1-5, we'll just show all active tokens for today.
        today = timezone.now().date()
        
        context['waiting_tokens'] = QueueToken.objects.filter(
            status='WAITING', created_at__date=today
        ).order_by('created_at')
        
        context['serving_tokens'] = QueueToken.objects.filter(
            status='SERVING', created_at__date=today
        ).order_by('-updated_at')
        
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
            
            QueueHistory.objects.create(
                token=token,
                changed_by=request.user,
                from_status=old_status,
                to_status=new_status,
                notes=f"Status changed to {new_status} via staff panel."
            )
            
            messages.success(request, f"Token {token.token_number} marked as {new_status}.")
            
        return redirect('queues:staff_manage')
