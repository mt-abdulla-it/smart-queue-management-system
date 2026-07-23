"""
Smart Queue Management System — Root URL Configuration.

Routes all incoming HTTP requests to the appropriate app.
URL patterns are organized by app with clear prefixes.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# =============================================================================
# Admin site customization
# =============================================================================
admin.site.site_header = 'Smart Queue Management System'
admin.site.site_title = 'SQMS Admin'
admin.site.index_title = 'Administration Panel'

# =============================================================================
# URL Patterns
# =============================================================================
urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # App URLs
    path('', include('apps.core.urls', namespace='core')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('branches/', include('apps.branches.urls', namespace='branches')),
    path('queues/', include('apps.queues.urls', namespace='queues')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('feedback/', include('apps.feedback.urls', namespace='feedback')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    # REST API (versioned)
    path('api/v1/', include('apps.api.v1.urls', namespace='api-v1')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# =============================================================================
# Debug toolbar and media files (development only)
# =============================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Django Debug Toolbar
    if 'debug_toolbar' in (settings.INSTALLED_APPS or []):
        try:
            import debug_toolbar  # noqa: F401
            urlpatterns += [
                path('__debug__/', include('debug_toolbar.urls')),
            ]
        except ImportError:
            pass
