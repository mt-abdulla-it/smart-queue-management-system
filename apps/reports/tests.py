from typing import Any
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.branches.models import Branch, Department, Service
from apps.queues.models import QueueToken

User = get_user_model()


class ReportsExportTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin_report',
            email='admin@report.com',
            password='password123',
            role='ADMIN'
        )
        self.branch = Branch.objects.create(name="Main Branch", code="MB-01")
        self.department = Department.objects.create(name="Customer Care", branch=self.branch)
        self.service = Service.objects.create(
            name="General Inquiry",
            prefix="GI",
            department=self.department,
            avg_service_time_minutes=10
        )
        self.token = QueueToken.objects.create(
            user=self.admin,
            service=self.service,
            token_number="GI-101",
            status="WAITING"
        )

    def test_export_csv_view_authenticated(self):
        self.client.login(username='admin_report', password='password123')
        response: Any = self.client.get(reverse('reports:export_csv'))
        self.assertEqual(getattr(response, 'status_code', None), 200)
        self.assertEqual(response.headers.get('Content-Type'), 'text/csv')
        self.assertIn('GI-101', response.content.decode('utf-8'))

