from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.branches.models import Branch, Department, Service
from apps.queues.models import QueueToken

User = get_user_model()

class TokenLiveStatusAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='Password123!',
            role='USER',
            first_name='Test',
            last_name='User'
        )
        self.branch = Branch.objects.create(name="Central Hospital", code="CH")
        self.department = Department.objects.create(name="OPD", branch=self.branch)
        self.service = Service.objects.create(
            name="General Consultation",
            department=self.department,
            prefix="GEN",
            avg_service_time_minutes=10
        )
        self.token = QueueToken.objects.create(
            user=self.user,
            service=self.service,
            token_number="GEN-001",
            status="WAITING",
            queue_date=timezone.now().date()
        )
        self.client = Client()

    def test_token_detail_view(self):
        self.client.login(email='testuser@example.com', password='Password123!')
        response = self.client.get(reverse('queues:token_detail', kwargs={'pk': self.token.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GEN-001')
        self.assertContains(response, 'Live Sync Active')

    def test_token_live_status_api(self):
        self.client.login(email='testuser@example.com', password='Password123!')
        response = self.client.get(reverse('queues:api_token_status', kwargs={'pk': self.token.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['token_number'], 'GEN-001')
        self.assertEqual(data['status'], 'WAITING')
        self.assertEqual(data['position'], 1)
        self.assertEqual(data['total_ahead'], 0)
        self.assertIn('progress_percent', data)
