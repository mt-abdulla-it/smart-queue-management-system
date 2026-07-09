"""
Dashboard Views — Stub for Phase 5 & 8.

Redirects users to their role-appropriate dashboard.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    """
    Dashboard home view — shows role-appropriate dashboard.
    Will be fully implemented in Phase 5 (Staff) and Phase 8 (Admin).
    """
    template_name = 'dashboard/home.html'

    def get_template_names(self):
        """Return the appropriate template based on user role."""
        user = self.request.user
        if user.role == 'ADMIN':
            return ['dashboard/admin_dashboard.html']
        elif user.role == 'STAFF':
            return ['dashboard/staff_dashboard.html']
        return ['dashboard/user_dashboard.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Dashboard'
        return context
