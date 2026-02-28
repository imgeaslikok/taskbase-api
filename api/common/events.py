import logging
from typing import Any

from .enums import EventType

_logger = logging.getLogger("api")


def log_event(level: int, event: EventType, **fields: Any) -> None:
    """
    Emit a structured application event log.

    Produces log lines in the form:
        event_name key=value key=value

    The request_id is injected automatically by the logging filter.
    """

    if fields:
        context = " ".join(f"{k}={v}" for k, v in fields.items())
        message = f"{event} {context}"
    else:
        message = str(event)

    _logger.log(level, message)
