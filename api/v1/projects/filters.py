import django_filters

from api.common.filters import TimestampRangeFilterSet
from apps.projects.models import Collaborator, Project, Task


class ProjectFilter(TimestampRangeFilterSet):
    """
    Filtering contract for Project list (API v1).
    Deterministic filters only; free-text search is handled by DRF SearchFilter.
    """

    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=Project._meta.get_field("status").choices,
    )
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    slug = django_filters.CharFilter(field_name="slug", lookup_expr="exact")
    owner_id = django_filters.NumberFilter(field_name="owner_id", lookup_expr="exact")

    class Meta:
        model = Project
        fields = ["status", "name", "slug", "owner_id"]


class TaskFilter(TimestampRangeFilterSet):
    """
    Filtering contract for Task list (API v1).

    Common filters:
    - status / priority
    - assignee (or unassigned)
    - due_date ranges
    """

    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=Task._meta.get_field("status").choices,
    )
    priority = django_filters.ChoiceFilter(
        field_name="priority",
        choices=Task._meta.get_field("priority").choices,
    )

    assignee_id = django_filters.NumberFilter(
        field_name="assignee_id", lookup_expr="exact"
    )

    # Convenience flag: /tasks/?unassigned=true
    unassigned = django_filters.BooleanFilter(method="filter_unassigned")

    due_date = django_filters.DateFilter(field_name="due_date", lookup_expr="exact")
    due_date_gte = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_date_lte = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")

    class Meta:
        model = Task
        fields = [
            "status",
            "priority",
            "assignee_id",
            "unassigned",
            "due_date",
            "due_date_gte",
            "due_date_lte",
        ]

    def filter_unassigned(self, queryset, name, value):
        if value is True:
            return queryset.filter(assignee__isnull=True)
        if value is False:
            return queryset.filter(assignee__isnull=False)
        return queryset


class CollaboratorFilter(TimestampRangeFilterSet):
    """
    Filtering contract for Collaborators (API v1).
    """

    role = django_filters.ChoiceFilter(
        field_name="role",
        choices=Collaborator._meta.get_field("role").choices,
    )
    user_id = django_filters.NumberFilter(field_name="user_id", lookup_expr="exact")

    class Meta:
        model = Collaborator
        fields = ["role", "user_id"]
