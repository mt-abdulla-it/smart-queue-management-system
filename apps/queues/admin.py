"""Queues admin."""
from django.contrib import admin
from .models import QueueToken, QueueHistory


class QueueHistoryInline(admin.TabularInline):
    model = QueueHistory
    extra = 0
    readonly_fields = ('action', 'action_by', 'notes', 'created_at')


@admin.register(QueueToken)
class QueueTokenAdmin(admin.ModelAdmin):
    list_display = ('token_number', 'user', 'service', 'branch', 'status', 'queue_date', 'position')
    list_filter = ('status', 'queue_date', 'branch', 'booking_type')
    search_fields = ('token_number', 'user__email', 'user__first_name')
    date_hierarchy = 'queue_date'
    inlines = [QueueHistoryInline]


@admin.register(QueueHistory)
class QueueHistoryAdmin(admin.ModelAdmin):
    list_display = ('token', 'action', 'action_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('token__token_number',)
