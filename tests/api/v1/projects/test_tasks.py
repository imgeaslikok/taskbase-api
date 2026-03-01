import threading
import time

import pytest
from concurrency_safe import lock
from django.db import connection
from rest_framework import status

from api.common.enums import ErrorCode
from apps.projects.enums import TaskStatus
from apps.projects.locks import task_status_lock_key
from apps.projects.models import Task
from tests.utils.api import unwrap_results
from tests.utils.assertions import assert_object_in_list
from tests.utils.db import close_default_connection


@pytest.mark.django_db
def test_tasks_list_requires_auth(api_client, task_urls):
    res = api_client.get(task_urls["list"])
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_tasks_list_ok(owner_client, task_urls):
    res = owner_client.get(task_urls["list"])
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_tasks_create_requires_auth(api_client, task_urls):
    payload = {
        "title": "T1",
        "description": "d",
        "status": "todo",
        "priority": "low",
        "position": 0,
    }
    res = api_client.post(task_urls["list"], payload, format="json")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_tasks_create_ok(owner_client, task_urls):
    payload = {
        "title": "T1",
        "description": "d",
        "status": "todo",
        "priority": "low",
        "position": 0,
    }
    res = owner_client.post(task_urls["list"], payload, format="json")
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data["title"] == "T1"
    assert "slug" in res.data

    assert_object_in_list(owner_client, task_urls["list"], res.data["slug"])


@pytest.mark.django_db
def test_tasks_filter_by_status_and_priority(owner_client, project, task_urls):
    # create directly in DB for deterministic filtering
    Task.objects.create(
        project=project,
        title="A",
        description="d",
        status="todo",
        priority="low",
        assignee=project.owner,
    )
    Task.objects.create(
        project=project,
        title="B",
        description="d",
        status="done",
        priority="high",
        assignee=project.owner,
    )

    res = owner_client.get(task_urls["list"] + "?status=todo&priority=low")
    assert res.status_code == status.HTTP_200_OK

    data = unwrap_results(res)

    assert len(data) == 1
    assert data[0]["title"] == "A"
    assert all(t["status"] == "todo" and t["priority"] == "low" for t in data)


@pytest.mark.django_db
def test_tasks_ordering_by_position(owner_client, project, task_urls):
    Task.objects.create(
        project=project,
        title="A",
        description="d",
        status="todo",
        priority="low",
        assignee=project.owner,
        position=2,
    )
    Task.objects.create(
        project=project,
        title="B",
        description="d",
        status="todo",
        priority="low",
        assignee=project.owner,
        position=1,
    )

    res = owner_client.get(task_urls["list"] + "?ordering=position")
    assert res.status_code == status.HTTP_200_OK

    data = unwrap_results(res)
    positions = [t["position"] for t in data]
    assert positions == sorted(positions)


@pytest.mark.django_db
def test_tasks_retrieve_ok(owner_client, task, task_urls):
    res = owner_client.get(task_urls["detail"](task.slug))
    assert res.status_code == status.HTTP_200_OK
    assert res.data["slug"] == task.slug


@pytest.mark.django_db
def test_tasks_retrieve_not_found(owner_client, task_urls):
    res = owner_client.get(task_urls["detail"]("does-not-exist"))
    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_task_status_patch_happy_path(owner_client, task_urls, task):
    """
    Sanity: PATCH updates status successfully (authenticated as project owner).
    """
    url = task_urls["detail"](task.slug)
    res = owner_client.patch(url, {"status": TaskStatus.DONE}, format="json")

    assert res.status_code == status.HTTP_200_OK, res.data
    assert res.data["status"] == TaskStatus.DONE


@pytest.mark.django_db(transaction=True)
def test_task_status_patch_returns_409_when_lock_is_held(owner_client, task_urls, task):
    """
    Integration: hold the same advisory lock key and attempt a concurrent status update.
    Expect 409 + stable error contract.

    Requires PostgreSQL (advisory locks).
    """
    if connection.vendor != "postgresql":
        pytest.skip("Requires PostgreSQL (advisory locks).")

    started = threading.Event()

    def holder():
        try:
            with lock(task_status_lock_key(task), timeout=1.0):
                started.set()
                time.sleep(1.5)  # > use-case timeout to force conflict
        finally:
            close_default_connection()

    t = threading.Thread(target=holder)
    t.start()

    assert started.wait(timeout=2.0), "Lock holder did not start in time"

    url = task_urls["detail"](task.slug)
    res = owner_client.patch(url, {"status": TaskStatus.DONE}, format="json")

    t.join(timeout=5.0)

    assert res.status_code == status.HTTP_409_CONFLICT, res.data
    assert "error" in res.data
    assert res.data["error"]["code"] == ErrorCode.CONCURRENCY_CONFLICT


@pytest.mark.django_db
def test_task_status_patch_idempotent(owner_client, task_urls, task):
    """
    If already DONE, setting DONE again should still succeed.
    """
    task.status = TaskStatus.DONE
    task.save(update_fields=["status"])

    url = task_urls["detail"](task.slug)
    res = owner_client.patch(url, {"status": TaskStatus.DONE}, format="json")

    assert res.status_code == status.HTTP_200_OK, res.data
    assert res.data["status"] == TaskStatus.DONE
