from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.branches.models import Branch, Department, Service
from apps.queues.models import QueueToken
from apps.accounts.models import User
import random

class Command(BaseCommand):
    help = 'Seeds the database with dummy data for presentation.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Seeding database...'))

        # 1. Create a Branch
        branch, created = Branch.objects.get_or_create(
            code='CGH',
            defaults={
                'name': 'Colombo General Hospital',
                'address': 'Ward Place, Colombo 07',
                'phone': '0112691111',
                'email': 'info@cgh.lk'
            }
        )

        # 1.5 Create a Dummy User for the Tokens
        dummy_user, _ = User.objects.get_or_create(
            email='patient@example.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'PATIENT'
            }
        )


        # 2. Create Departments
        opd, _ = Department.objects.get_or_create(
            code='OPD', branch=branch,
            defaults={'name': 'Outpatient Department', 'description': 'General consultations'}
        )
        cardio, _ = Department.objects.get_or_create(
            code='CARD', branch=branch,
            defaults={'name': 'Cardiology Unit', 'description': 'Heart related checkups'}
        )

        # 3. Create Services
        svc_gen, _ = Service.objects.get_or_create(
            name='General Checkup', department=opd, code='GEN01',
            defaults={'prefix': 'GEN', 'avg_service_time_minutes': 10}
        )
        svc_blood, _ = Service.objects.get_or_create(
            name='Blood Test', department=opd, code='BLD01',
            defaults={'prefix': 'BLD', 'avg_service_time_minutes': 5}
        )
        svc_ecg, _ = Service.objects.get_or_create(
            name='ECG', department=cardio, code='ECG01',
            defaults={'prefix': 'ECG', 'avg_service_time_minutes': 15}
        )

        # 4. Generate Tokens for the last 7 days (to populate the Admin Chart)
        if QueueToken.objects.count() < 10:
            today = timezone.now()
            services = [svc_gen, svc_blood, svc_ecg]
            
            for i in range(7):  # Last 7 days
                day = today - timedelta(days=i)
                num_tokens = random.randint(15, 45) # Random amount of patients per day
                
                for j in range(num_tokens):
                    service = random.choice(services)
                    token = QueueToken.objects.create(
                        service=service,
                        branch=branch,
                        user=dummy_user,
                        queue_date=day.date(),
                        token_number=f"{service.prefix}-{j+1:03d}",
                        status='COMPLETED' if i > 0 else random.choice(['WAITING', 'SERVING', 'COMPLETED'])
                    )
                    # Manually override created_at since auto_now_add usually overrides it
                    QueueToken.objects.filter(id=token.id).update(created_at=day)

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))
