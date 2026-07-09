"""
Report Model.

Stores metadata about generated reports (PDF, Excel).
"""
from django.conf import settings
from django.db import models
from core.models import TimeStampedModel


class Report(TimeStampedModel):
    """Tracks generated reports."""

    class ReportType(models.TextChoices):
        DAILY = 'DAILY', 'Daily Report'
        WEEKLY = 'WEEKLY', 'Weekly Report'
        MONTHLY = 'MONTHLY', 'Monthly Report'
        CUSTOM = 'CUSTOM', 'Custom Report'

    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                      null=True, related_name='generated_reports')
    title = models.CharField('Report Title', max_length=200)
    report_type = models.CharField(max_length=10, choices=ReportType.choices)
    start_date = models.DateField('Start Date')
    end_date = models.DateField('End Date')
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='reports')
    file = models.FileField('Report File', upload_to='reports/')
    generated_at = models.DateTimeField('Generated At', auto_now_add=True)

    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-generated_at']

    def __str__(self):
        return f'{self.title} ({self.get_report_type_display()})'
