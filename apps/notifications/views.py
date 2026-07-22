"""
Notifications Views.
"""
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    """View to see all notifications for the current user."""
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-sent_at')


class MarkNotificationReadView(LoginRequiredMixin, View):
    """Mark a single notification as read."""
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'is_read': True})
            
        messages.success(request, 'Notification marked as read.')
        return redirect('notifications:list')


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    """Mark all notifications for the user as read."""
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:list')


class DeleteNotificationView(LoginRequiredMixin, View):
    """Delete a single notification."""
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        messages.success(request, 'Notification removed.')
        return redirect('notifications:list')
