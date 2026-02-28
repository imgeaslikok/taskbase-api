from django.db import models
from django.utils import timezone

from . import managers, querysets


class TimeStampedModel(models.Model):
    """Timestamp fields or Audit fields"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # new table won't be created


class SoftDeleteModel(models.Model):
    """Soft delete"""

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = managers.SoftDeleteManager()
    all_objects = querysets.SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        if self.deleted_at is None:
            self.deleted_at = timezone.now()
            self.save(update_fields=["deleted_at"])

    def restore(self):
        if self.deleted_at is not None:
            self.deleted_at = None
            self.save(update_fields=["deleted_at"])

    def hard_delete(self):
        return super().delete()


class TimeStampedSoftDeleteModel(TimeStampedModel, SoftDeleteModel):
    """Convenience base"""

    class Meta:
        abstract = True
