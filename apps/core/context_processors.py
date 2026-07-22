"""
Core Context Processors.

These functions inject variables into every template context,
making site-wide data available without passing it manually.
"""
from django.conf import settings


def site_settings(request):
    """
    Inject site-wide settings into every template.

    Available in templates as:
        {{ site_name }}
        {{ site_url }}
        {{ current_year }}
        {{ unread_notifications_count }}
        {{ recent_notifications }}
    """
    from datetime import datetime

    context = {
        'site_name': getattr(settings, 'SITE_NAME', 'Smart Queue Management System'),
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'current_year': datetime.now().year,
        'debug': settings.DEBUG,
    }

    # Add unread notification count and recent notifications for authenticated users
    if request.user.is_authenticated:
        try:
            from apps.notifications.models import Notification
            user_notifications = Notification.objects.filter(user=request.user)
            context['unread_notifications_count'] = user_notifications.filter(is_read=False).count()
            context['recent_notifications'] = user_notifications.order_by('-sent_at')[:5]
        except Exception:
            context['unread_notifications_count'] = 0
            context['recent_notifications'] = []

    return context
