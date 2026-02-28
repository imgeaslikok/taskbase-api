import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from apps.projects.models import Collaborator, Project, Task


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()

@pytest.fixture
def project_urls():
    """
    Central registry for project endpoint URLs used by API v1 tests.
    """
    return {
        "list": "/api/v1/projects/",
        "detail": lambda slug: f"/api/v1/projects/{slug}/",
    }


@pytest.fixture
def project(user):
    return Project.objects.create(
        owner=user,
        name="P1",
        description="d",
        status="active",
    )


@pytest.fixture
def task_urls(project):
    return {
        "list": f"/api/v1/projects/{project.slug}/tasks/",
        "detail": lambda task_slug: (
            f"/api/v1/projects/{project.slug}/tasks/{task_slug}/"
        ),
    }


@pytest.fixture
def collaborator_urls(project):
    return {
        "list": f"/api/v1/projects/{project.slug}/collaborators/",
        "detail": lambda user_id: (
            f"/api/v1/projects/{project.slug}/collaborators/{user_id}/"
        ),
    }


@pytest.fixture
def task(project, user):
    return Task.objects.create(
        project=project,
        title="T1",
        description="d",
        status="todo",
        priority="low",
        assignee=user,
        position=0,
    )


@pytest.fixture
def user2(db):
    """
    Second user used for collaborator tests.
    """
    User = get_user_model()
    password = "StrongPass123!"

    username_field = getattr(User, "USERNAME_FIELD", "username")
    value = "user2@example.com" if username_field == "email" else "user2"

    u = User.objects.create_user(**{username_field: value}, password=password)
    u.is_active = True
    u.save(update_fields=["is_active"])
    return u


@pytest.fixture
def collaborator(project, user2):
    return Collaborator.objects.create(project=project, user=user2, role="viewer")


# RBAC helpers


@pytest.fixture
def viewer(user2, project):
    """
    A project collaborator with viewer role.
    """
    Collaborator.objects.create(project=project, user=user2, role="viewer")
    return user2


@pytest.fixture
def developer(db, project):
    """
    A project collaborator with developer role.
    """
    User = get_user_model()
    password = "StrongPass123!"

    username_field = getattr(User, "USERNAME_FIELD", "username")
    value = "dev@example.com" if username_field == "email" else "dev"

    u = User.objects.create_user(**{username_field: value}, password=password)
    u.is_active = True
    u.save(update_fields=["is_active"])

    Collaborator.objects.create(project=project, user=u, role="developer")
    return u


@pytest.fixture
def maintainer(db, project):
    """
    A project collaborator with maintainer role.
    """
    User = get_user_model()
    password = "StrongPass123!"

    username_field = getattr(User, "USERNAME_FIELD", "username")
    value = "maintainer@example.com" if username_field == "email" else "maintainer"

    u = User.objects.create_user(**{username_field: value}, password=password)
    u.is_active = True
    u.save(update_fields=["is_active"])

    Collaborator.objects.create(project=project, user=u, role="maintainer")
    return u


@pytest.fixture
def owner(project):
    """
    The project owner.
    """
    return project.owner


@pytest.fixture
def viewer_client(api_client, viewer):
    """
    Authenticated client as viewer.
    """
    api_client.force_authenticate(user=viewer)
    return api_client


@pytest.fixture
def developer_client(api_client, developer):
    """
    Authenticated client as developer.
    """
    api_client.force_authenticate(user=developer)
    return api_client


@pytest.fixture
def maintainer_client(api_client, maintainer):
    """
    Authenticated client as maintainer.
    """
    api_client.force_authenticate(user=maintainer)
    return api_client


@pytest.fixture
def owner_client(api_client, owner):
    """
    Authenticated client as owner.
    """
    api_client.force_authenticate(user=owner)
    return api_client
