from rest_framework.pagination import PageNumberPagination


class DefaultPageNumberPagination(PageNumberPagination):
    """
    Default pagination for list endpoints.

    Provides:
    - Consistent pagination contract
    - Client-controlled page size (optional)
    - Upper bound to prevent excessive load
    """

    page_size = 20

    # allows: ?page_size=50
    page_size_query_param = "page_size"

    # prevents abuse: ?page_size=100000
    max_page_size = 100
