from .models import Task

TASK_STATUS_LOCK_KEY_TEMPLATE = "taskbase:task:{task.pk}:transition:status"


def task_status_lock_key(task: Task) -> str:
    """
    Canonical advisory lock key for serializing task status transitions.
    """
    return TASK_STATUS_LOCK_KEY_TEMPLATE.format(task=task)
