"""Accounts models — will be fully implemented in Phase 2."""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Custom user manager that uses email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model using email as the primary identifier.

    Roles:
        ADMIN: Full system access
        STAFF: Queue management access
        USER: Queue booking access
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        STAFF = 'STAFF', 'Staff Member'
        USER = 'USER', 'Regular User'

    # Remove username field, use email instead
    username = None
    email = models.EmailField('Email Address', unique=True)
    phone = models.CharField('Phone Number', max_length=15, blank=True)
    nic = models.CharField('NIC Number', max_length=20, blank=True,
                           help_text='National Identity Card number')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    is_email_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_staff_member(self):
        return self.role == self.Role.STAFF


class StaffProfile(TimeStampedModel):
    """Extended profile for staff members with branch/department assignment."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField('Employee ID', max_length=20, unique=True)
    designation = models.CharField(max_length=100, blank=True)
    branch = models.ForeignKey(
        'branches.Branch', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='staff_members'
    )
    department = models.ForeignKey(
        'branches.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='staff_members'
    )
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.employee_id}'
