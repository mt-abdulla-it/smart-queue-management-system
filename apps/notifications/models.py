"""
Notification Model.

Stores all notifications sent to users (email, SMS, push, in-app).
"""
from django.conf import settings
from django.db import models
from core.models import TimeStampedModel


class Notification(TimeStampedModel):
    """Tracks all notifications sent to users."""

    class NotificationType(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        PUSH = 'PUSH', 'Push Notification'
        IN_APP = 'IN_APP', 'In-App'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='notifications')
    title = models.CharField('Title', max_length=200)
    message = models.TextField('Message')
    notification_type = models.CharField(max_length=10, choices=NotificationType.choices,
                                          default=NotificationType.IN_APP)
    is_read = models.BooleanField('Read', default=False)
    sent_at = models.DateTimeField('Sent At', auto_now_add=True)
    read_at = models.DateTimeField('Read At', null=True, blank=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-sent_at']

    def __str__(self):
        return f'{self.title} → {self.user.email}'
