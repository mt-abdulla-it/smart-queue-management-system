"""
Notifications signals.
Triggers emails, persistent notifications, and WebSocket events when queue status changes.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.queues.models import QueueHistory
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
            print(f"WebSocket broadcast failed: {e}")
    
    # 2. Notification handling for user
    if not token.user:
        return
        
    user_email = token.user.email
    subject = None
    message = None

    if action == QueueHistory.Action.CREATED:
        subject = f"Queue Booked: {token.token_number}"
        message = f"Hello {token.user.first_name},\n\nYou have successfully booked token {token.token_number} for {token.service.name} at {token.branch.name}.\n\nThank you for using Smart Queue."
    elif action in [QueueHistory.Action.CALLED, QueueHistory.Action.SERVING]:
        subject = f"Your Turn: {token.token_number}"
        message = f"Hello {token.user.first_name},\n\nIt is now your turn! Please proceed to counter for {token.service.name}.\n\nThank you for using Smart Queue."
    elif action == QueueHistory.Action.COMPLETED:
        subject = f"Service Completed: {token.token_number}"
        message = f"Hello {token.user.first_name},\n\nYour service for token {token.token_number} has been completed. Thank you!"
    elif action == QueueHistory.Action.SKIPPED:
        subject = f"Token Skipped: {token.token_number}"
        message = f"Hello {token.user.first_name},\n\nYour token {token.token_number} was skipped. Please approach staff if you are present."
    elif action == QueueHistory.Action.ON_HOLD:
        subject = f"Token On Hold: {token.token_number}"
        message = f"Hello {token.user.first_name},\n\nYour token {token.token_number} has been put on hold."
    elif action == QueueHistory.Action.CANCELLED:
        subject = f"Token Cancelled: {token.token_number}"
        message = f"Hello {token.user.first_name},\n\nYour token {token.token_number} has been cancelled."

    if subject and message:
        # Create persistent In-App notification
        Notification.objects.create(
            user=token.user,
            title=subject,
            message=message,
            notification_type=Notification.NotificationType.IN_APP
        )
        
        # Send Email
        try:
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@sqms.lk'),
                [user_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send notification email to {user_email}: {e}")
