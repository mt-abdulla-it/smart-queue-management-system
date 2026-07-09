"""
Smart Queue Management System — WSGI Configuration.

Standard WSGI application for deployment with Gunicorn or similar
WSGI servers. Note: WebSocket support requires ASGI (see asgi.py).
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_wsgi_application()
