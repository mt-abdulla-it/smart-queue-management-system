"""
Smart Queue Management System — Development Settings.

Extends base.py with development-specific overrides:
- DEBUG = True
- Console email backend
- Django Debug Toolbar
- In-memory channel layer (optional fallback)
"""
from .base import *  # noqa: F401, F403

# =============================================================================
# DEBUG
# =============================================================================

DEBUG = True

# =============================================================================
# ALLOWED HOSTS
# =============================================================================

ALLOWED_HOSTS = ['*']

# =============================================================================
# INSTALLED APPS (add dev tools)
# =============================================================================

INSTALLED_APPS += [  # noqa: F405
    'django_extensions',
]

# Only add debug toolbar if it's installed
try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(  # noqa: F405
        MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,  # noqa: F405
        'debug_toolbar.middleware.DebugToolbarMiddleware'
    )
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
except ImportError:
    pass

# =============================================================================
# EMAIL (Console output for development)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# CORS (Allow all in development)
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = True

# =============================================================================
# CSRF
# =============================================================================

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# =============================================================================
# STATIC FILES (No compression in dev)
# =============================================================================

STORAGES = {
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# =============================================================================
# CHANNELS (Fallback to in-memory if Redis is not available)
# =============================================================================

# Uncomment to use in-memory channel layer (no Redis needed):
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels.layers.InMemoryChannelLayer',
#     },
# }

# =============================================================================
# LOGGING (More verbose in development)
# =============================================================================

LOGGING['loggers']['apps']['level'] = 'DEBUG'  # noqa: F405
