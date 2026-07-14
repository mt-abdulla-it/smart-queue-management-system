"""
Notifications signals.
Triggers emails and WebSocket events when queue status changes.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.queues.models import QueueHistory, QueueToken
from .models import Notification

@receiver(post_save, sender=QueueHistory)
def handle_queue_status_change(sender, instance, created, **kwargs):
    if not created:
        return
        
    token = instance.token
    action = instance.action
    
    # 1. Trigger WebSocket Event for Live Display
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        try:
            async_to_sync(channel_layer.group_send)(
                'live_queue',
                {
                    'type': 'queue_update',
                    'message': f'Token {token.token_number} action: {action}',
                    'token_number': token.token_number,
                    'status': token.status,
                    'service': token.service.name
                }
            )
        except Exception as e:
            print(f"WebSocket broadcast failed (Redis might be down): {e}")
    
    # 2. Trigger Email Notification (if user exists)
    if not token.user:
        return
        
    user_email = token.user.email
    
    if action == 'SERVING':
        subject = f"Your Turn: {token.token_number}"
        message = f"Hello {token.user.first_name},\n\nIt is your turn! Please proceed to the counter for {token.service.name} at {token.service.department.branch.name}.\n\nThank you for using Smart Queue."
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=True,
            )
            # Create persistent notification
            Notification.objects.create(
                user=token.user,
                title=subject,
                message=message,
                notification_type='EMAIL'
            )
        except Exception as e:
            print(f"Failed to send email to {user_email}: {e}")
            
    elif action == 'CREATED':
        # E.g., someone booked online.
        subject = f"Queue Booked: {token.token_number}"
        message = f"Hello {token.user.first_name},\n\nYou have successfully booked {token.token_number} for {token.service.name}.\n\nThank you for using Smart Queue."
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=True,
            )
            # Create persistent notification
            Notification.objects.create(
                user=token.user,
                title=subject,
                message=message,
                notification_type='EMAIL'
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

