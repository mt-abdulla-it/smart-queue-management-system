"""
Core View Mixins.

Reusable mixins for Django class-based views that enforce
role-based access control and provide common functionality.

Classes:
    RoleRequiredMixin: Restricts view access to specific user roles.
    AdminRequiredMixin: Restricts access to admin users only.
    StaffRequiredMixin: Restricts access to staff users only.
    AjaxResponseMixin: Adds AJAX/JSON response capability.
"""
import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect

logger = logging.getLogger('apps')


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin that restricts access to users with specific roles.

    Usage:
        class MyView(RoleRequiredMixin, View):
            allowed_roles = ['ADMIN', 'STAFF']
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        """Check if user has the required role before dispatching."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if self.allowed_roles and request.user.role not in self.allowed_roles:
            messages.error(
                request,
                'You do not have permission to access this page.'
            )
            logger.warning(
                f'Access denied: User {request.user.email} (role={request.user.role}) '
                f'attempted to access {request.path}'
            )
            return redirect('dashboard:home')

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    """Restricts access to admin users only."""
    allowed_roles = ['ADMIN']


class StaffRequiredMixin(RoleRequiredMixin):
    """Restricts access to staff and admin users."""
    allowed_roles = ['ADMIN', 'STAFF']


class AjaxResponseMixin:
    """
    Mixin that provides AJAX response capabilities for views.

    If the request is AJAX (XMLHttpRequest), returns JSON.
    Otherwise, returns the standard HTML response.
    """

    def is_ajax(self, request):
        """Check if the request is an AJAX request."""
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def json_response(self, data, status=200):
        """Return a JSON response."""
        return JsonResponse(data, status=status)

    def json_error(self, message, status=400, errors=None):
        """Return a JSON error response."""
        response_data = {'success': False, 'message': message}
        if errors:
            response_data['errors'] = errors
        return JsonResponse(response_data, status=status)

    def json_success(self, message='Success', data=None):
        """Return a JSON success response."""
        response_data = {'success': True, 'message': message}
        if data:
            response_data['data'] = data
        return JsonResponse(response_data)


class PaginationMixin:
    """
    Mixin that provides configurable pagination for list views.

    Usage:
        class MyListView(PaginationMixin, ListView):
            paginate_by = 20
    """
    paginate_by = 20

    def get_paginate_by(self, queryset):
        """Allow page size to be set via query parameter."""
        page_size = self.request.GET.get('page_size', self.paginate_by)
        try:
            page_size = int(page_size)
            # Limit max page size to prevent abuse
            return min(page_size, 100)
        except (ValueError, TypeError):
            return self.paginate_by
