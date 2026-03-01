from rest_framework import status
from rest_framework.exceptions import APIException

from api.common.enums import ErrorCode


class ConcurrencyConflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = ErrorCode.CONCURRENCY_CONFLICT
    default_detail = "Task is being updated concurrently. Please retry."
