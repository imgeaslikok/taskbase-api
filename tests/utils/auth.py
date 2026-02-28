import base64
import json


def decode_jwt_payload(token: str) -> dict:
    """
    Decode JWT payload (2nd segment). JWT payload is base64url-encoded JSON.
    Intended for test verification only.
    """
    payload_b64 = token.split(".")[1]
    payload_b64 += "=" * (-len(payload_b64) % 4)
    return json.loads(base64.urlsafe_b64decode(payload_b64))
