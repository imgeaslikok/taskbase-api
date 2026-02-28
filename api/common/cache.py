import hashlib
from functools import wraps
from typing import Callable

from django.core.cache import cache
from rest_framework.response import Response


def cache_list_response(*, ttl: int, prefix: str) -> Callable:
    """
    Cache a DRF list response safely.

    Key includes:
    - user id (prevents tenant leaks)
    - full path (captures query params: search/order/page)
    """

    def decorator(view_method: Callable) -> Callable:
        @wraps(view_method)
        def wrapped(self, request, *args, **kwargs):
            raw_key = f"{prefix}:user={request.user.id}:path={request.get_full_path()}"
            cache_key = f"api:{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()}"

            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

            response = view_method(self, request, *args, **kwargs)

            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout=ttl)

            return response

        return wrapped

    return decorator
