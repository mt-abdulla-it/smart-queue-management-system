"""
Core Abstract Models.

These abstract base models provide common fields and behavior
that all other models in the system can inherit from. This ensures
consistency and reduces code duplication across apps.

Classes:
    TimeStampedModel: Adds created_at and updated_at timestamps.
    SoftDeleteModel: Adds soft-delete functionality (is_deleted flag).
"""
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.

    All models in the project should inherit from this
    to maintain consistent audit timestamps.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the record was created.'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the record was last updated.'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteManager(models.Manager):
    """
    Custom manager that filters out soft-deleted records by default.
    Use .all_with_deleted() to include deleted records.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        """Return all records including soft-deleted ones."""
        return super().get_queryset()

    def deleted_only(self):
        """Return only soft-deleted records."""
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract model that provides soft-delete functionality.

    Instead of permanently deleting records, they are marked
    with is_deleted=True. This is important for audit trails
    and data integrity in a queue management system.
    """
    is_deleted = models.BooleanField(
        default=False,
        help_text='Soft-delete flag. If True, the record is considered deleted.'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when the record was soft-deleted.'
    )

    # Custom manager that excludes deleted records by default
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Fallback manager that includes everything

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark this record as deleted."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])


class UUIDModel(models.Model):
    """
    Abstract model that uses UUID as the primary key.
    Useful for models exposed via API where sequential IDs
    could leak information about record counts.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier (UUID).'
    )

    class Meta:
        abstract = True
