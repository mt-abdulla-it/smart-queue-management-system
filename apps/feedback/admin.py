"""Feedback admin."""
from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'rating', 'is_resolved', 'created_at')
    list_filter = ('rating', 'is_resolved', 'branch')
    search_fields = ('user__email', 'comment')
