"""Reports admin."""
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'branch', 'start_date', 'end_date', 'generated_by', 'generated_at')
    list_filter = ('report_type', 'branch')
    search_fields = ('title',)
