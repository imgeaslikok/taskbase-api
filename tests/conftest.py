import pytest
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_urls():
    return {
        "login": "/api/v1/auth/login/",
        "refresh": "/api/v1/auth/refresh/",
        "logout": "/api/v1/auth/logout/",
        "current_user": "/api/v1/auth/me/",
    }


@pytest.fixture
def login_payload(user):
    User = type(user)
    username_field = getattr(User, "USERNAME_FIELD", "username")
    return {
        username_field: getattr(user, username_field),
        "password": user.raw_password,
    }


@pytest.fixture
def token_pair(api_client, login_payload, auth_urls):
    res = api_client.post(auth_urls["login"], login_payload, format="json")
    assert res.status_code == status.HTTP_200_OK, res.data
    return {"access": res.data["access"], "refresh": res.data["refresh"]}


@pytest.fixture
def user(db):
    """
    Create an active user compatible with:
    - default Django User (USERNAME_FIELD="username")
    - custom user model (USERNAME_FIELD="email", etc.)

    Adds `raw_password` for convenience in tests.
    """
    User = get_user_model()
    password = "StrongPass123!"

    username_field = getattr(User, "USERNAME_FIELD", "username")
    value = "test@example.com" if username_field == "email" else "testuser"

    u = User.objects.create_user(**{username_field: value}, password=password)
    u.is_active = True
    u.save(update_fields=["is_active"])

    u.raw_password = password
    return u


@pytest.fixture
def auth_client(api_client, token_pair, user):
    """
    APIClient authenticated with Authorization: Bearer <access>.
    """
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_pair['access']}")
    api_client.test_user = user
    return api_client
