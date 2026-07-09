"""
Core Views.

Handles the public-facing homepage and any site-wide views.
"""
from django.shortcuts import redirect
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    Public homepage view.

    If the user is authenticated, redirects to their appropriate dashboard.
    Otherwise, shows the public landing page.
    """
    template_name = 'core/home.html'

    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to their dashboard."""
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
