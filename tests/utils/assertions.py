from .api import unwrap_results


def assert_valid_access_token(data: dict) -> None:
    assert set(data.keys()) == {"access"}

    access = data["access"]

    assert isinstance(access, str) and access
    assert access.count(".") == 2


def assert_valid_token_pair(data: dict) -> None:
    """
    Assert that response contains a valid JWT access/refresh pair.

    Ensures:
    - exact keys present
    - values are non-empty strings
    - values look like JWTs (header.payload.signature)
    """
    assert isinstance(data, dict), "Token response must be a dict"

    expected_keys = {"access", "refresh"}
    actual_keys = set(data.keys())

    assert actual_keys == expected_keys, (
        f"Token response keys mismatch. Expected {expected_keys}, got {actual_keys}"
    )

    access = data["access"]
    refresh = data["refresh"]

    assert isinstance(access, str) and access, "Access token must be non-empty string"
    assert isinstance(refresh, str) and refresh, (
        "Refresh token must be non-empty string"
    )

    # JWT format sanity check
    assert access.count(".") == 2, "Access token is not valid JWT format"
    assert refresh.count(".") == 2, "Refresh token is not valid JWT format"


def assert_object_in_list(auth_client, list_url: str, slug: str) -> None:
    """
    Assert that an object with given slug appears in list endpoint.
    """
    res = auth_client.get(list_url)
    assert res.status_code == 200

    slugs = [obj["slug"] for obj in unwrap_results(res)]

    assert slug in slugs, f"{slug} not found in list response"
