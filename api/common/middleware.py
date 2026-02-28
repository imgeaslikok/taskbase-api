import logging
import re
import threading
import time
import uuid

from django.utils.deprecation import MiddlewareMixin

access_logger = logging.getLogger("api")

_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9\-_.]{8,128}$")
_request_ctx = threading.local()


def get_request_id() -> str | None:
    """Return the active request id for the current thread (if any)."""
    return getattr(_request_ctx, "request_id", None)


class RequestIdMiddleware(MiddlewareMixin):
    """
    Ensure every request/response carries a correlation id (X-Request-ID).

    - Reuse incoming X-Request-ID when valid (proxy/gateway friendly).
    - Otherwise generate a new id.
    - Expose it via request.request_id, response header, and thread-local context.
    """

    header_name = "HTTP_X_REQUEST_ID"  # WSGI-mapped header key
    response_header = "X-Request-ID"

    def process_request(self, request):
        incoming = request.META.get(self.header_name, "")
        request_id = self._normalize(incoming) or uuid.uuid4().hex

        request.request_id = request_id
        _request_ctx.request_id = request_id  # enables request_id in logs

    def process_response(self, request, response):
        request_id = getattr(request, "request_id", None) or uuid.uuid4().hex

        response[self.response_header] = request_id
        _request_ctx.request_id = None  # avoid leaking context across requests

        return response

    def process_exception(self, request, exception):
        # Make sure the context is cleared even on errors.
        _request_ctx.request_id = None
        return None

    def _normalize(self, value: str) -> str | None:
        value = (value or "").strip()
        if not value:
            return None
        return value if _REQUEST_ID_RE.match(value) else None


class AccessLogMiddleware(MiddlewareMixin):
    """Log method/path/status/duration for each request."""

    def process_request(self, request):
        request._start_ts = time.monotonic()

    def process_response(self, request, response):
        start = getattr(request, "_start_ts", None)
        if start is not None:
            duration_ms = int((time.monotonic() - start) * 1000)
            access_logger.info(
                "request method=%s path=%s status=%s duration_ms=%s",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
            )
        return response
