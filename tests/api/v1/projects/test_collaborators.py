import pytest
from rest_framework import status

from apps.projects.models import Collaborator


@pytest.mark.django_db
def test_collaborators_list_requires_auth(api_client, collaborator_urls):
    res = api_client.get(collaborator_urls["list"])
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_collaborators_list_ok(auth_client, collaborator_urls):
    res = auth_client.get(collaborator_urls["list"])
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_collaborators_add_ok(auth_client, project, user2, collaborator_urls):
    payload = {"user_id": user2.id, "role": "developer"}
    res = auth_client.post(collaborator_urls["list"], payload, format="json")
    assert res.status_code == status.HTTP_201_CREATED

    c = Collaborator.objects.get(project=project, user=user2)
    assert c.role == "developer"
    assert c.deleted_at is None


@pytest.mark.django_db
def test_collaborators_add_same_user_twice_is_idempotent(
    auth_client, project, user2, collaborator_urls
):
    Collaborator.objects.create(project=project, user=user2, role="viewer")

    payload = {"user_id": user2.id, "role": "developer"}
    res = auth_client.post(collaborator_urls["list"], payload, format="json")

    assert res.status_code == status.HTTP_200_OK

    c = Collaborator.objects.get(project=project, user=user2)
    assert c.role == "developer"
    assert c.deleted_at is None


@pytest.mark.django_db
def test_collaborators_readd_restores_soft_deleted(
    auth_client, project, user2, collaborator_urls
):
    c = Collaborator.objects.create(project=project, user=user2, role="viewer")
    c.delete()
    c.refresh_from_db()
    assert c.deleted_at is not None

    payload = {"user_id": user2.id, "role": "developer"}
    res = auth_client.post(collaborator_urls["list"], payload, format="json")

    # restore (not new create) -> 200 OK
    assert res.status_code == status.HTTP_200_OK

    # should restore same row (count stays 1)
    assert Collaborator.all_objects.filter(project=project, user=user2).count() == 1

    c.refresh_from_db()
    assert c.deleted_at is None
    assert c.role == "developer"
