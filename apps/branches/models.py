"""
Branches Models — Branch, Department, and Service.

These represent the organizational hierarchy:
Branch → Department → Service

Each service generates its own queue tokens with a unique prefix.
"""
from django.db import models
from core.models import TimeStampedModel


class Branch(TimeStampedModel):
    """
    Represents a physical location (hospital or government office).

    Each branch can have multiple departments and services.
    """
    name = models.CharField('Branch Name', max_length=200)
    code = models.CharField('Branch Code', max_length=20, unique=True,
                            help_text='Unique code for the branch (e.g., CMB-GH)')
    address = models.TextField('Address')
    city = models.CharField('City', max_length=100)
    district = models.CharField('District', max_length=100)
    phone = models.CharField('Phone', max_length=15, blank=True)
    email = models.EmailField('Email', blank=True)
    latitude = models.DecimalField('Latitude', max_digits=10, decimal_places=7,
                                   null=True, blank=True)
    longitude = models.DecimalField('Longitude', max_digits=10, decimal_places=7,
                                    null=True, blank=True)
    is_active = models.BooleanField('Active', default=True)
    operating_hours = models.CharField('Operating Hours', max_length=100,
                                       default='8:00 AM - 4:00 PM',
                                       help_text='e.g., 8:00 AM - 4:00 PM')
    image = models.ImageField('Branch Image', upload_to='branches/', blank=True, null=True)

    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class Department(TimeStampedModel):
    """
    Represents a department within a branch.

    Each department offers specific services.
    """
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField('Department Name', max_length=200)
    code = models.CharField('Department Code', max_length=20)
    description = models.TextField('Description', blank=True)
    is_active = models.BooleanField('Active', default=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
        unique_together = ['branch', 'code']

    def __str__(self):
        return f'{self.name} - {self.branch.name}'


class Service(TimeStampedModel):
    """
    Represents a service offered by a department.

    Each service has a unique token prefix (e.g., A, B, C)
    and manages its own queue of tokens.
    """
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='services')
    name = models.CharField('Service Name', max_length=200)
    code = models.CharField('Service Code', max_length=20)
    description = models.TextField('Description', blank=True)
    prefix = models.CharField('Token Prefix', max_length=5,
                               help_text='Prefix for queue tokens (e.g., A, B, C)')
    avg_service_time_minutes = models.PositiveIntegerField(
        'Avg Service Time (min)', default=10,
        help_text='Average time to serve one customer in minutes'
    )
    max_daily_tokens = models.PositiveIntegerField(
        'Max Daily Tokens', default=100,
        help_text='Maximum tokens that can be issued per day'
    )
    current_token_number = models.PositiveIntegerField('Current Token Number', default=0)
    is_active = models.BooleanField('Active', default=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['name']
        unique_together = ['department', 'code']

    def __str__(self):
        return f'{self.name} ({self.prefix})'

    def reset_daily_counter(self):
        """Reset the daily token counter to 0. Called at start of each day."""
        self.current_token_number = 0
        self.save(update_fields=['current_token_number'])

    def get_next_token_number(self):
        """Get the next sequential token number and increment counter."""
        self.current_token_number += 1
        self.save(update_fields=['current_token_number'])
        return self.current_token_number
