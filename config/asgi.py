"""
Smart Queue Management System — ASGI Configuration.

Configures the ASGI application with Django Channels for
handling both HTTP and WebSocket connections.

WebSocket routing is handled by config.routing.
"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Initialize Django ASGI application early to ensure AppRegistry is populated
django_asgi_app = get_asgi_application()

# Import WebSocket URL patterns after Django is initialized
from config.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    # HTTP requests are handled by Django's standard ASGI application
    'http': django_asgi_app,

    # WebSocket connections are authenticated and routed
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
