import pytest
from rest_framework import status

from apps.projects.models import Project
from tests.utils.api import unwrap_results
from tests.utils.assertions import assert_object_in_list


@pytest.mark.django_db
def test_projects_list_requires_auth(api_client, project_urls):
    res = api_client.get(project_urls["list"])
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_projects_list_ok(auth_client, project_urls):
    res = auth_client.get(project_urls["list"])
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_projects_create_requires_auth(api_client, project_urls):
    payload = {"name": "CRM", "description": "Sales", "status": "active"}
    res = api_client.post(project_urls["list"], payload, format="json")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_projects_create_ok(auth_client, project_urls):
    payload = {"name": "CRM", "description": "Sales", "status": "active"}
    res = auth_client.post(project_urls["list"], payload, format="json")
    assert res.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    # create serializer returns these fields
    assert res.data["name"] == "CRM"
    assert "slug" in res.data

    assert_object_in_list(auth_client, project_urls["list"], res.data["slug"])


@pytest.mark.django_db
def test_projects_filter_by_status(auth_client, project_urls):
    Project.objects.create(owner=auth_client.test_user, name="A", description="d", status="active")
    Project.objects.create(owner=auth_client.test_user, name="B", description="d", status="archived")

    res = auth_client.get(project_urls["list"] + "?status=active")
    assert res.status_code == status.HTTP_200_OK

    data = unwrap_results(res)
    assert all(item["status"] == "active" for item in data)


@pytest.mark.django_db
def test_projects_ordering_by_name(auth_client, project_urls):
    Project.objects.create(owner=auth_client.test_user, name="Zeta", description="d", status="active")
    Project.objects.create(owner=auth_client.test_user, name="Alpha", description="d", status="active")

    res = auth_client.get(project_urls["list"] + "?ordering=name")
    assert res.status_code == status.HTTP_200_OK

    data = unwrap_results(res)
    names = [p["name"] for p in data]
    assert names == sorted(names)


@pytest.mark.django_db
def test_projects_search(auth_client, project_urls):
    Project.objects.create(
        owner=auth_client.test_user, name="CRM System", description="Sales", status="active"
    )
    Project.objects.create(
        owner=auth_client.test_user, name="Mobile App", description="iOS", status="active"
    )

    res = auth_client.get(project_urls["list"] + "?search=crm")
    assert res.status_code == status.HTTP_200_OK

    data = unwrap_results(res)
    assert len(data) == 1
    assert data[0]["name"] == "CRM System"


@pytest.mark.django_db
def test_projects_list_includes_counts(auth_client, project_urls):
    """
    ProjectListSerializer should expose tasks_count & collaborators_count.
    """
    Project.objects.create(owner=auth_client.test_user, name="A", description="d", status="active")

    res = auth_client.get(project_urls["list"])
    assert res.status_code == status.HTTP_200_OK

    data = unwrap_results(res)
    assert len(data) >= 1
    assert "tasks_count" in data[0]
    assert "collaborators_count" in data[0]
