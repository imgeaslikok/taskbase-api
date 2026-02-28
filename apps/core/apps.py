from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Core application providing reusable model infrastructure.

    This app defines abstract base models and mixins implementing common
    persistence patterns, including:

    - Abstract base models for shared fields and behavior
    - Timestamp fields for auditing
    - Soft delete pattern with custom managers and querysets
    - Slug-based URL identifiers
    - Reusable model mixins
    - Database constraints and indexing support

    These components serve as the foundation for the domain model layer
    and ensure consistency, maintainability, and scalability.
    """

    name = "apps.core"
