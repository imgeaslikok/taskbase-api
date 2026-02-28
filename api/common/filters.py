import django_filters


class TimestampRangeFilterSet(django_filters.FilterSet):
    """
    Base FilterSet for timestamp range filtering.

    Query params:
      - created_at_after, created_at_before
      - updated_at_after, updated_at_before
    """

    created_at_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    updated_at_after = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gte"
    )
    updated_at_before = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="lte"
    )
