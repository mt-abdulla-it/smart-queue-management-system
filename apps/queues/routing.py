from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/queues/live/$', consumers.QueueConsumer.as_asgi()),
]
