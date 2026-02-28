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
    assert res.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    c = Collaborator.objects.get(project=project, user=user2)
    assert c.role == "developer"


@pytest.mark.django_db
def test_collaborators_add_same_user_twice_fails(
    auth_client, project, user2, collaborator_urls
):
    Collaborator.objects.create(project=project, user=user2, role="viewer")

    payload = {"user_id": user2.id, "role": "developer"}
    res = auth_client.post(collaborator_urls["list"], payload, format="json")

    # Depending on how you handle IntegrityError, this could be status.HTTP_400_BAD_REQUEST or 409
    assert res.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT)
