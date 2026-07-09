"""
Feedback Views.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from apps.core.mixins import RoleRequiredMixin

from .models import Feedback
from .forms import FeedbackForm

class FeedbackSubmitView(LoginRequiredMixin, CreateView):
    """View for users to submit feedback."""
    model = Feedback
    form_class = FeedbackForm
    template_name = 'feedback/submit.html'
    success_url = reverse_lazy('dashboard:user')

    def form_valid(self, form):
        feedback = form.save(commit=False)
        feedback.user = self.request.user
        feedback.save()
        messages.success(self.request, 'Thank you for your feedback!')
        return super().form_valid(form)


class AdminFeedbackListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """View for admins to see all feedback."""
    model = Feedback
    template_name = 'feedback/admin_list.html'
    context_object_name = 'feedbacks'
    allowed_roles = ['ADMIN']
    
    def get_queryset(self):
        return Feedback.objects.select_related('user', 'branch').order_by('-created_at')
