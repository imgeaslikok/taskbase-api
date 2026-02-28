from django.db import models

from .querysets import SoftDeleteQuerySet


class SoftDeleteManager(models.Manager):
    """Default manager restriction"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).active()
