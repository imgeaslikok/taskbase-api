from enum import StrEnum


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
