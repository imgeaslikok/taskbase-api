"""
Project domain use-cases.

Use-cases orchestrate domain state transitions without coupling to DRF.

Concurrency control is implemented via PostgreSQL advisory locks using
django-concurrency-safe.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from concurrency_safe import concurrency_safe
from django.db import transaction

from .enums import TaskStatus
from .exceptions import InvalidTaskStatus, TaskConcurrencyError
from .locks import TASK_STATUS_LOCK_KEY_TEMPLATE
from .models import Collaborator, Project, Task

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


def _raise_task_conflict(*_args, **_kwargs) -> None:
    """
    Adapter for django-concurrency-safe.

    Converts lock acquisition failure into a domain-level exception.
    """
    raise TaskConcurrencyError("Task is being updated concurrently. Please retry.")


@dataclass(frozen=True)
class TransitionTaskStatusResult:
    """
    Result of a task status transition.

    Attributes:
        task: The updated task instance.
        idempotent: True if no state change was required.
    """

    task: Task
    idempotent: bool


@concurrency_safe(
    key=TASK_STATUS_LOCK_KEY_TEMPLATE,
    timeout=1.0,
    on_conflict=_raise_task_conflict,
)
def transition_task_status(*, task: Task, to_status: str) -> TransitionTaskStatusResult:
    """
    Concurrency-safe task status transition.

    Guarantees:

    - Serializes all transitions for a task under one advisory lock.
    - Ensures idempotency.
    - Refreshes state from DB after acquiring lock to avoid stale writes.
    """

    if to_status not in {s for s, _ in TaskStatus.choices}:
        raise InvalidTaskStatus("Invalid status.")

    # ensure fresh state after lock acquisition
    task.refresh_from_db(fields=["status", "deleted_at", "updated_at"])

    if task.status == to_status:
        return TransitionTaskStatusResult(task=task, idempotent=True)

    task.status = to_status
    task.save(update_fields=["status", "updated_at"])

    return TransitionTaskStatusResult(task=task, idempotent=False)


@dataclass(frozen=True)
class AddCollaboratorResult:
    collaborator: Collaborator
    created: bool
    restored: bool
    role_updated: bool


@transaction.atomic
def add_collaborator(
    *, project: Project, user: AbstractBaseUser, role: str
) -> AddCollaboratorResult:
    """
    Add a collaborator to a project.

    Behavior:
    - if missing: create
    - if soft-deleted: restore + set role
    - if active: update role if needed (idempotent)
    """
    qs = getattr(Collaborator, "all_objects", Collaborator.objects)
    collab = qs.filter(project=project, user=user).first()

    if collab is None:
        collab = Collaborator.objects.create(project=project, user=user, role=role)
        return AddCollaboratorResult(
            collaborator=collab, created=True, restored=False, role_updated=False
        )

    restored = False
    role_updated = False

    if getattr(collab, "deleted_at", None):
        # restore() should set deleted_at=None and save
        collab.restore()
        restored = True

    if collab.role != role:
        collab.role = role
        collab.save(update_fields=["role", "updated_at"])
        role_updated = True

    return AddCollaboratorResult(
        collaborator=collab, created=False, restored=restored, role_updated=role_updated
    )
