import pytest
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from tests.utils.assertions import assert_valid_token_pair
from tests.utils.auth import decode_jwt_payload
from tests.utils.http import HTTP_400_OR_401


@pytest.mark.django_db
def test_login_success_returns_access_and_refresh(api_client, login_payload, auth_urls):
    res = api_client.post(auth_urls["login"], login_payload, format="json")
    assert res.status_code == status.HTTP_200_OK
    assert_valid_token_pair(res.data)


@pytest.mark.django_db
def test_login_wrong_credentials(api_client, login_payload, auth_urls):
    bad = dict(login_payload)
    bad["password"] = "WRONG_PASSWORD"
    res = api_client.post(auth_urls["login"], bad, format="json")
    assert res.status_code in HTTP_400_OR_401


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload",
    [
        {},  # no fields
        {"username": "a"},  # missing password
        {"password": "x"},  # missing username
    ],
)
def test_login_missing_fields_returns_400(api_client, auth_urls, payload):
    res = api_client.post(auth_urls["login"], payload, format="json")
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_current_user_requires_auth(api_client, auth_urls):
    res = api_client.get(auth_urls["current_user"])
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_current_user_ok(auth_client, auth_urls):
    res = auth_client.get(auth_urls["current_user"])
    assert res.status_code == status.HTTP_200_OK
    assert "id" in res.data


@pytest.mark.django_db
def test_refresh_rotation_blacklists_old_refresh(
    api_client, token_pair, auth_urls, settings
):
    settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] = True
    settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] = True

    old_refresh = token_pair["refresh"]
    old_token = RefreshToken(old_refresh)

    r1 = api_client.post(auth_urls["refresh"], {"refresh": old_refresh}, format="json")
    assert r1.status_code == status.HTTP_200_OK
    assert_valid_token_pair(r1.data)

    new_refresh = r1.data["refresh"]
    assert new_refresh != old_refresh

    # DB side-effect: old refresh is blacklisted after rotation
    assert BlacklistedToken.objects.filter(token__jti=old_token["jti"]).exists()

    r2 = api_client.post(auth_urls["refresh"], {"refresh": old_refresh}, format="json")
    assert r2.status_code in HTTP_400_OR_401

    r3 = api_client.post(auth_urls["refresh"], {"refresh": new_refresh}, format="json")
    assert r3.status_code == status.HTTP_200_OK
    assert_valid_token_pair(r3.data)


@pytest.mark.django_db
def test_refresh_requires_refresh_in_body(api_client, auth_urls):
    res = api_client.post(auth_urls["refresh"], {}, format="json")
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    "bad_refresh",
    [
        "not-a-jwt",
        "abc.def",  # wrong segments
        "abc.def.ghi",  # looks like jwt but garbage
    ],
)
def test_refresh_invalid_token_returns_400_or_401(api_client, auth_urls, bad_refresh):
    res = api_client.post(auth_urls["refresh"], {"refresh": bad_refresh}, format="json")
    assert res.status_code in HTTP_400_OR_401


@pytest.mark.django_db
def test_logout_blacklists_refresh(api_client, auth_client, token_pair, auth_urls):
    """
    Logout revokes refresh token so it can't mint new access tokens anymore.
    Also asserts DB side-effect: token is blacklisted.
    """
    refresh = token_pair["refresh"]
    token = RefreshToken(refresh)

    out = auth_client.post(auth_urls["logout"], {"refresh": refresh}, format="json")
    assert out.status_code == status.HTTP_204_NO_CONTENT

    # DB side-effect: blacklisted row created for this refresh token
    assert BlacklistedToken.objects.filter(token__jti=token["jti"]).exists()

    # same refresh cannot be used after logout
    r = api_client.post(auth_urls["refresh"], {"refresh": refresh}, format="json")
    assert r.status_code in HTTP_400_OR_401


@pytest.mark.django_db
def test_logout_requires_refresh_in_body(auth_client, auth_urls):
    res = auth_client.post(auth_urls["logout"], {}, format="json")
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    "bad_refresh",
    [
        "not-a-jwt",
        "abc.def",
        "abc.def.ghi",
    ],
)
def test_logout_invalid_refresh_returns_400_or_401(auth_client, auth_urls, bad_refresh):
    res = auth_client.post(auth_urls["logout"], {"refresh": bad_refresh}, format="json")
    assert res.status_code in HTTP_400_OR_401


@pytest.mark.django_db
def test_claims_hygiene_access_token_minimal(token_pair):
    """
    Ensure we do not leak sensitive fields via JWT claims.
    """
    claims = decode_jwt_payload(token_pair["access"])

    # Expected baseline claims (SimpleJWT)
    assert "exp" in claims
    assert claims.get("token_type") == "access"
    assert "user_id" in claims

    # No sensitive claims
    forbidden = {"password", "password_hash", "secret", "api_key"}
    assert forbidden.isdisjoint(set(claims.keys()))
