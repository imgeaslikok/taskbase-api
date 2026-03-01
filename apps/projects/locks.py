from .models import Task


def task_status_lock_key(task: Task) -> str:
    """
    Canonical advisory lock key for serializing task status transitions.
    """
    return f"taskbase:task:{task.pk}:transition:status"
