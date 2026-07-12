"""Accounts signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StaffProfile

@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.STAFF:
        # Create a basic staff profile, employee_id can be generated or updated later
        StaffProfile.objects.create(
            user=instance,
            employee_id=f"EMP-{instance.id:04d}"
        )
