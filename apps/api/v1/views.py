"""
API v1 Views.
"""
from rest_framework import viewsets, permissions
from apps.queues.models import QueueToken
from .serializers import QueueTokenSerializer

class QueueTokenViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows tokens to be viewed.
    """
    serializer_class = QueueTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own tokens via API unless they are staff
        user = self.request.user
        if user.role in ['ADMIN', 'STAFF']:
            return QueueToken.objects.all().order_by('-created_at')
        return QueueToken.objects.filter(user=user).order_by('-created_at')
