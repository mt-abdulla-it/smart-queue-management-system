"""
Dashboard Views.
Provides the Admin, Staff, and User dashboard entry points.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg, F
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView
from datetime import timedelta
import json

from apps.core.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.branches.models import Branch
from apps.queues.models import QueueToken
from apps.feedback.models import Feedback

class HomeRedirectView(LoginRequiredMixin, TemplateView):
    """Redirects authenticated users to their specific role dashboard."""
    template_name = 'dashboard/home.html'

    def get(self, request, *args, **kwargs):
        role = request.user.role
        if role == 'ADMIN':
            return redirect('dashboard:admin')
        elif role == 'STAFF':
            return redirect('queues:staff_manage')
        else:
            return redirect('dashboard:user')

class UserDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for regular users."""
    template_name = 'dashboard/user_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # User Stats
        context['active_tokens'] = QueueToken.objects.filter(user=user, status__in=['WAITING', 'SERVING']).count()
        context['completed_tokens'] = QueueToken.objects.filter(user=user, status='COMPLETED').count()
        context['feedback_given'] = Feedback.objects.filter(user=user).count()
        
        # Recent Tokens
        context['recent_tokens'] = QueueToken.objects.filter(user=user).order_by('-created_at')[:5]
        
        return context

class AdminDashboardView(RoleRequiredMixin, TemplateView):
    """Dashboard for Administrators with real-time analytics."""
    template_name = 'dashboard/admin_dashboard.html'
    allowed_roles = ['ADMIN']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Key Metrics
        context['total_users'] = User.objects.filter(role='USER').count()
        context['today_tokens'] = QueueToken.objects.filter(created_at__date=today).count()
        context['active_branches'] = Branch.objects.filter(is_active=True).count()
        
        avg_rating = Feedback.objects.aggregate(Avg('rating'))['rating__avg']
        context['avg_rating'] = round(avg_rating, 1) if avg_rating else "N/A"
        
        # Chart Data (Last 7 Days)
        labels = []
        data = []
        
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime("%a"))
            count = QueueToken.objects.filter(created_at__date=day).count()
            data.append(count)
            
        context['chart_labels'] = json.dumps(labels)
        context['chart_data'] = json.dumps(data)
        
        return context
