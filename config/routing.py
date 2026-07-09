"""
Smart Queue Management System — WebSocket URL Routing.

Defines all WebSocket URL patterns for the project.
"""
import apps.queues.routing

# Combine WebSocket URL patterns from all apps
websocket_urlpatterns = []
websocket_urlpatterns += apps.queues.routing.websocket_urlpatterns
