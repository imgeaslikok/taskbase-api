import secrets

from django.db import models
from django.utils.text import slugify


class SlugMixin(models.Model):
    """
    Abstract mixin that adds an auto-generated, unique slug for URL identification.

    Subclasses must implement `get_slug_source()` to provide the value used
    for slug generation. The slug is created only once and remains stable.
    """

    slug = models.SlugField(
        max_length=256,
        unique=True,
        blank=True,
        db_index=True,
        help_text="Unique, URL-friendly identifier.",
    )

    class Meta:
        abstract = True

    def get_slug_source(self) -> str:
        """Return the string used to generate the slug."""
        raise NotImplementedError

    def generate_slug(self) -> str:
        base = slugify(self.get_slug_source())
        suffix = secrets.token_hex(4)  # 8 hex chars
        return f"{base}-{suffix}"

    def save(self, *args, **kwargs):
        """Generate slug on first save if not provided."""
        if not self.slug:
            self.slug = self.generate_slug()

        super().save(*args, **kwargs)
