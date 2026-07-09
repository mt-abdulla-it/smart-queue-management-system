"""
Smart Queue Management System — Production Settings.

Extends base.py with production security hardening:
- DEBUG = False
- HTTPS enforcement
- Secure cookies
- HSTS headers
- Proper email backend
"""
from .base import *  # noqa: F401, F403

# =============================================================================
# DEBUG
# =============================================================================

DEBUG = False

# =============================================================================
# SECURITY — HTTPS Enforcement
# =============================================================================

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# =============================================================================
# SECURITY — Cookies
# =============================================================================

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# =============================================================================
# SECURITY — Headers
# =============================================================================

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# EMAIL (Production SMTP)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# =============================================================================
# CORS (Restrict in production)
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list(  # noqa: F405
    'CORS_ALLOWED_ORIGINS',
    default=['https://smartqueue.lk']
)

# =============================================================================
# LOGGING (Production — errors only to file)
# =============================================================================

LOGGING['handlers']['console']['filters'] = ['require_debug_false']  # noqa: F405
LOGGING['handlers']['console']['level'] = 'ERROR'  # noqa: F405
