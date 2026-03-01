"""
Project domain use-cases.

Use-cases orchestrate domain state transitions without coupling to DRF.

Concurrency control is implemented via PostgreSQL advisory locks using
django-concurrency-safe.
"""

from __future__ import annotations

from dataclasses import dataclass

from concurrency_safe import concurrency_safe

from .enums import TaskStatus
from .exceptions import InvalidTaskStatus, TaskConcurrencyError
from .models import Task
from .locks import TASK_STATUS_LOCK_KEY_TEMPLATE


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
