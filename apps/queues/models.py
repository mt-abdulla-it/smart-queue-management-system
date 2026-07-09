"""
Queue Models — QueueToken and QueueHistory.

The core models for the queue management system.
QueueToken tracks each customer's position and status.
QueueHistory provides a complete audit trail.
"""
from django.conf import settings
from django.db import models
from apps.core.models import TimeStampedModel


class QueueToken(TimeStampedModel):
    """
    Represents a single queue token issued to a customer.

    Lifecycle: WAITING → CALLED → SERVING → COMPLETED
    Alternative: WAITING → CANCELLED / NO_SHOW / ON_HOLD
    """

    class Status(models.TextChoices):
        WAITING = 'WAITING', 'Waiting'
        CALLED = 'CALLED', 'Called'
        SERVING = 'SERVING', 'Serving'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        NO_SHOW = 'NO_SHOW', 'No Show'
        ON_HOLD = 'ON_HOLD', 'On Hold'

    class BookingType(models.TextChoices):
        ONLINE = 'ONLINE', 'Online Booking'
        WALK_IN = 'WALK_IN', 'Walk-in'
        KIOSK = 'KIOSK', 'Kiosk'

    token_number = models.CharField('Token Number', max_length=20,
                                     help_text='e.g., A-001, B-042')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='queue_tokens')
    service = models.ForeignKey('branches.Service', on_delete=models.CASCADE,
                                related_name='tokens')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE,
                                related_name='tokens')
    called_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='called_tokens',
                                   help_text='Staff member who called this token')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.WAITING)
    position = models.PositiveIntegerField('Queue Position', default=0)
    queue_date = models.DateField('Queue Date')
    booked_at = models.DateTimeField('Booked At', auto_now_add=True)
    called_at = models.DateTimeField('Called At', null=True, blank=True)
    serving_at = models.DateTimeField('Serving At', null=True, blank=True)
    completed_at = models.DateTimeField('Completed At', null=True, blank=True)
    estimated_wait_minutes = models.PositiveIntegerField('Estimated Wait (min)', default=0)
    qr_code = models.ImageField('QR Code', upload_to='qr_codes/', blank=True, null=True)
    notes = models.TextField('Notes', blank=True)
    booking_type = models.CharField(max_length=10, choices=BookingType.choices,
                                     default=BookingType.ONLINE)
    is_priority = models.BooleanField('Priority', default=False)

    class Meta:
        verbose_name = 'Queue Token'
        verbose_name_plural = 'Queue Tokens'
        ordering = ['queue_date', 'position']
        unique_together = ['token_number', 'queue_date', 'branch']
        indexes = [
            models.Index(fields=['queue_date', 'status']),
            models.Index(fields=['branch', 'queue_date']),
            models.Index(fields=['user', 'queue_date']),
        ]

    def __str__(self):
        return f'{self.token_number} - {self.get_status_display()}'


class QueueHistory(TimeStampedModel):
    """
    Audit trail for queue token state changes.

    Every action on a token is logged here for accountability
    and reporting purposes.
    """

    class Action(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        CALLED = 'CALLED', 'Called'
        SERVING = 'SERVING', 'Serving'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        SKIPPED = 'SKIPPED', 'Skipped'
        ON_HOLD = 'ON_HOLD', 'Put On Hold'
        RECALLED = 'RECALLED', 'Recalled'

    token = models.ForeignKey(QueueToken, on_delete=models.CASCADE, related_name='history')
    action_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, related_name='queue_actions')
    action = models.CharField(max_length=15, choices=Action.choices)
    notes = models.TextField('Notes', blank=True)

    class Meta:
        verbose_name = 'Queue History'
        verbose_name_plural = 'Queue History'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.token.token_number} - {self.get_action_display()}'
