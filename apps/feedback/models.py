"""
Feedback Model.

Allows users to submit feedback about their queue experience.
"""
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from apps.core.models import TimeStampedModel


class Feedback(TimeStampedModel):
    """User feedback with star rating and comments."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='feedbacks')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE,
                                related_name='feedbacks', null=True, blank=True)
    service = models.ForeignKey('branches.Service', on_delete=models.CASCADE,
                                 related_name='feedbacks', null=True, blank=True)
    rating = models.PositiveIntegerField(
        'Rating',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 (poor) to 5 (excellent)'
    )
    comment = models.TextField('Comment', blank=True)
    admin_response = models.TextField('Admin Response', blank=True)
    is_resolved = models.BooleanField('Resolved', default=False)

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-created_at']

    def __str__(self):
        return f'Feedback by {self.user.email} - {self.rating}★'
