import logging

from django.conf import settings
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .enums import ErrorCode

logger = logging.getLogger("django.request")


STATUS_TO_ERROR_CODE = {
    status.HTTP_400_BAD_REQUEST: ErrorCode.VALIDATION_ERROR,
    status.HTTP_401_UNAUTHORIZED: ErrorCode.AUTHENTICATION_FAILED,
    status.HTTP_403_FORBIDDEN: ErrorCode.PERMISSION_DENIED,
    status.HTTP_404_NOT_FOUND: ErrorCode.NOT_FOUND,
    status.HTTP_409_CONFLICT: ErrorCode.CONCURRENCY_CONFLICT,
}


def core_exception_handler(exc, context):
    """
    Centralized API exception handler.

    Ensures all errors follow a consistent contract and include request_id
    for traceability across logs and clients.

    Principles:
    - Delegate to DRF for known exceptions.
    - Normalize response structure.
    - Never leak internals unless DEBUG=True.
    - Always attach request_id when available.
    """

    request = context.get("request")
    request_id = getattr(request, "request_id", None)

    # Let DRF handle expected exceptions first.
    response = exception_handler(exc, context)

    if response is None:
        return _handle_unexpected_error(exc, request_id)

    return Response(
        {
            "error": {
                "code": _map_status_to_code(response.status_code),
                "message": _extract_message(response.data),
                # Preserve field-level validation details for clients.
                "details": response.data if isinstance(response.data, dict) else {},
                "request_id": request_id,
            }
        },
        status=response.status_code,
    )


def _handle_unexpected_error(exc, request_id):
    """
    Handle non-DRF exceptions (typically 500-class).
    Converts them into safe, client-friendly responses.
    """

    if isinstance(exc, IntegrityError):
        return Response(
            {
                "error": {
                    "code": "integrity_error",
                    "message": "Database integrity error.",
                    "details": {},
                    "request_id": request_id,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Keep details out of the API response, but log full stack trace.
    logger.exception("unhandled_exception")

    # Hide internal details in production for security.
    message = str(exc) if settings.DEBUG else "Internal server error."

    return Response(
        {
            "error": {
                "code": "server_error",
                "message": message,
                "details": {},
                "request_id": request_id,
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _map_status_to_code(status_code):

    return STATUS_TO_ERROR_CODE.get(
        status_code,
        ErrorCode.SERVER_ERROR,
    )


def _extract_message(data):
    """
    Extract a concise human-readable message from DRF error payload.
    Prefers the first meaningful validation error when present.
    """

    if isinstance(data, dict) and data:
        value = next(iter(data.values()))

        if isinstance(value, list) and value:
            return str(value[0])

        return str(value)

    return str(data)
