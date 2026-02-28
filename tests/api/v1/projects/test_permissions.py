import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    (
        ("viewer_client", status.HTTP_200_OK),
        ("developer_client", status.HTTP_200_OK),
        ("maintainer_client", status.HTTP_200_OK),
        ("owner_client", status.HTTP_200_OK),
    ),
)
def test_task_list_rbac(request, task_urls, client_fixture, expected_status):
    client = request.getfixturevalue(client_fixture)
    res = client.get(task_urls["list"])
    assert res.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    (
        ("viewer_client", status.HTTP_403_FORBIDDEN),
        ("developer_client", status.HTTP_201_CREATED),
        ("maintainer_client", status.HTTP_201_CREATED),
        ("owner_client", status.HTTP_201_CREATED),
    ),
)
def test_task_create_rbac(request, task_urls, client_fixture, expected_status):
    client = request.getfixturevalue(client_fixture)

    payload = {
        "title": "New Task",
        "description": "d",
        "status": "todo",
        "priority": "low",
        "position": 1,
        "assignee_id": None,
    }

    res = client.post(task_urls["list"], payload, format="json")
    assert res.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    (
        ("viewer_client", status.HTTP_403_FORBIDDEN),
        ("developer_client", status.HTTP_200_OK),
        ("maintainer_client", status.HTTP_200_OK),
        ("owner_client", status.HTTP_200_OK),
    ),
)
def test_task_update_rbac(request, task_urls, task, client_fixture, expected_status):
    client = request.getfixturevalue(client_fixture)

    res = client.patch(
        task_urls["detail"](task.slug),
        {"title": "Updated"},
        format="json",
    )
    assert res.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    (
        ("viewer_client", status.HTTP_403_FORBIDDEN),
        ("developer_client", status.HTTP_204_NO_CONTENT),
        ("maintainer_client", status.HTTP_204_NO_CONTENT),
        ("owner_client", status.HTTP_204_NO_CONTENT),
    ),
)
def test_task_delete_rbac(request, task_urls, task, client_fixture, expected_status):
    client = request.getfixturevalue(client_fixture)

    res = client.delete(task_urls["detail"](task.slug))
    assert res.status_code == expected_status
