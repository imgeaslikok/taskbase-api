from .middleware import get_request_id


class RequestIdFilter:
    """Attach request_id to every log record when available."""

    def filter(self, record):
        record.request_id = get_request_id() or "-"
        return True
