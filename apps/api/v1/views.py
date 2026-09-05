"""
API v1 Views.
"""
from rest_framework import viewsets, permissions, status as http_status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.urls import reverse
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


class QueueTokenVerifyAPIView(APIView):
    """
    API v1 endpoint to verify a scanned token or token number.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        query = request.data.get('query') or request.data.get('token_number') or request.data.get('token_query')
        if not query:
            return Response({'detail': 'Token query or QR payload is required.'}, status=http_status.HTTP_400_BAD_REQUEST)

        import re
        token = None
        query = str(query).strip()

        if '/queues/token/' in query or '/queues/verify/' in query:
            match = re.search(r'/(?:token|verify)/(\d+)/?', query)
            if match:
                token = QueueToken.objects.filter(pk=int(match.group(1))).first()

        if not token and query.isdigit():
            token = QueueToken.objects.filter(pk=int(query)).first()

        if not token:
            token = QueueToken.objects.filter(
                token_number__iexact=query
            ).order_by('-created_at').first()

        if not token:
            return Response({'detail': f'Token matching "{query}" not found.'}, status=http_status.HTTP_404_NOT_FOUND)

        serializer = QueueTokenSerializer(token, context={'request': request})
        return Response({
            'valid': (token.queue_date == timezone.now().date()),
            'token': serializer.data,
            'verify_url': request.build_absolute_uri(reverse('queues:verify_token', kwargs={'pk': token.pk}))
        })

