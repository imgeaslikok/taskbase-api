from __future__ import annotations

from typing import Callable, Optional

from rest_framework.permissions import BasePermission

from apps.core.rbac import Scope
from apps.projects.policies import (
    COLLABORATOR_RULES,
    PROJECT_RULES,
    TASK_RULES,
)

SAFE_ACTIONS = {"list", "retrieve"}
WRITE_ACTIONS = {"create", "update", "partial_update"}
DELETE_ACTIONS = {"destroy"}

RuleCheck = Callable[[Scope[str]], bool]


class ProjectScopedRBACPermission(BasePermission):
    """
    Generic DRF permission adapter for project-scoped RBAC rules.

    Requires ProjectScopedMixin to set on request (before permission checks):
      - request.project_role: str | None
      - request.is_project_owner: bool

    Subclasses provide:
      - rules: RBACRules[str] instance (imported from apps.projects.policies)
    """

    rules = None  # RBACRules[str] instance

    message = "You do not have permission to perform this action."

    # Optional overrides (defaults bind to rules.*)
    write_check: Optional[RuleCheck] = None
    delete_check: Optional[RuleCheck] = None

    def has_permission(self, request, view) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False

        role = getattr(request, "project_role", None)
        bypass = getattr(request, "is_project_owner", None)

        # Fail closed if scope is missing (usually a wiring mistake).
        if bypass is None or self.rules is None:
            return False

        scope = Scope[str](role=role, bypass=bool(bypass))
        check = self._resolve_check(getattr(view, "action", None))

        if check is None:
            return False

        return bool(check(scope))

    def has_object_permission(self, request, view, obj) -> bool:
        # If object is project-scoped, enforce project match.
        if hasattr(obj, "project_id") or hasattr(obj, "project"):
            req_project = getattr(request, "project", None)
            obj_project_id = getattr(obj, "project_id", None) or getattr(
                getattr(obj, "project", None), "id", None
            )

            # If it's project-scoped and request.project missing -> deny (wiring bug)
            if req_project is None or obj_project_id is None:
                return False

            if getattr(req_project, "id", None) != obj_project_id:
                return False

        return self.has_permission(request, view)

    def _resolve_check(self, action: str | None) -> Optional[RuleCheck]:
        if not action:
            return None

        if action in SAFE_ACTIONS:
            return self.rules.can_read

        if action in WRITE_ACTIONS:
            return self.write_check or self.rules.can_write

        if action in DELETE_ACTIONS:
            return self.delete_check or self.rules.can_delete

        extra = self.extra_actions()
        return extra.get(action) if extra else None

    def extra_actions(self) -> dict[str, RuleCheck]:
        """Override to support custom DRF actions."""
        return {}


class TaskPermission(ProjectScopedRBACPermission):
    """RBAC for /projects/{project_slug}/tasks/ endpoints."""

    rules = TASK_RULES
    message = "You do not have access to tasks in this project."


class CollaboratorPermission(ProjectScopedRBACPermission):
    """RBAC for /projects/{project_slug}/collaborators/ endpoints."""

    rules = COLLABORATOR_RULES
    message = "You do not have access to collaborators in this project."

    # Collaborator create/update are management operations.
    write_check = COLLABORATOR_RULES.can_manage

    def extra_actions(self) -> dict[str, RuleCheck]:
        return {
            # Optional custom actions if you add them later
            "set_role": self.rules.can_manage,
            "change_role": self.rules.can_manage,
            "update_role": self.rules.can_manage,
        }


class ProjectNestedPermission(ProjectScopedRBACPermission):
    """
    RBAC for project-scoped project endpoints if you ever expose them.
    Example:
      /projects/{project_slug}/settings/
    """

    rules = PROJECT_RULES
    message = "You do not have access to this project."
