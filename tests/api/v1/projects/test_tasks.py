import pytest
from rest_framework import status

from apps.projects.models import Task
from tests.utils.api import unwrap_results
from tests.utils.assertions import assert_object_in_list


@pytest.mark.django_db
def test_tasks_list_requires_auth(api_client, task_urls):
    res = api_client.get(task_urls["list"])
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_tasks_list_ok(auth_client, task_urls):
    res = auth_client.get(task_urls["list"])
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
def test_tasks_create_ok(auth_client, task_urls):
    payload = {
        "title": "T1",
        "description": "d",
        "status": "todo",
        "priority": "low",
        "position": 0,
    }
    res = auth_client.post(task_urls["list"], payload, format="json")
    assert res.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
    assert res.data["title"] == "T1"
    assert "slug" in res.data

    assert_object_in_list(auth_client, task_urls["list"], res.data["slug"])


@pytest.mark.django_db
def test_tasks_filter_by_status_and_priority(auth_client, project, task_urls):
    # Create directly in DB for deterministic filtering
    Task.objects.create(
        project=project,
        title="A",
        description="d",
        status="todo",
        priority="low",
        assignee=auth_client.test_user,
    )
    Task.objects.create(
        project=project,
        title="B",
        description="d",
        status="done",
        priority="high",
        assignee=auth_client.test_user,
    )

    res = auth_client.get(task_urls["list"] + "?status=todo&priority=low")
    assert res.status_code == status.HTTP_200_OK

    data = unwrap_results(res)

    assert len(data) == 1
    assert data[0]["title"] == "A"
    assert all(t["status"] == "todo" and t["priority"] == "low" for t in data)


@pytest.mark.django_db
def test_tasks_ordering_by_position(auth_client, project, task_urls):
    Task.objects.create(
        project=project,
        title="A",
        description="d",
        status="todo",
        priority="low",
        assignee=auth_client.test_user,
        position=2,
    )
    Task.objects.create(
        project=project,
        title="B",
        description="d",
        status="todo",
        priority="low",
        assignee=auth_client.test_user,
        position=1,
    )

    res = auth_client.get(task_urls["list"] + "?ordering=position")
    assert res.status_code == status.HTTP_200_OK

    data = unwrap_results(res)
    positions = [t["position"] for t in data]
    assert positions == sorted(positions)


@pytest.mark.django_db
def test_tasks_retrieve_ok(auth_client, task, task_urls):
    res = auth_client.get(task_urls["detail"](task.slug))
    assert res.status_code == status.HTTP_200_OK
    assert res.data["slug"] == task.slug


@pytest.mark.django_db
def test_tasks_retrieve_not_found(auth_client, task_urls):
    res = auth_client.get(task_urls["detail"]("does-not-exist"))
    assert res.status_code == status.HTTP_404_NOT_FOUND
