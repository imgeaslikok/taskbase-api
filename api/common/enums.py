from enum import StrEnum


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_FAILED = "authentication_failed"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    INTEGRITY_ERROR = "integrity_error"
    CONCURRENCY_CONFLICT = "concurrency_conflict"
    SERVER_ERROR = "server_error"


class EventType(StrEnum):
    """
    Stable identifiers for application log events.

    These values form part of the observability contract.
    Avoid renaming existing events in production systems.
    """

    # Auth
    AUTH_LOGIN_SUCCESS = "auth_login_success"
    AUTH_LOGIN_FAILED = "auth_login_failed"

    # Project lifecycle
    PROJECT_CREATED = "project_created"
    PROJECT_DELETED = "project_deleted"

    # Collaborators
    COLLABORATOR_ADDED = "collaborator_added"
    COLLABORATOR_ROLE_CHANGED = "collaborator_role_changed"
    COLLABORATOR_REMOVED = "collaborator_removed"

    # Tasks
    TASK_CREATED = "task_created"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_MOVED = "task_moved"
