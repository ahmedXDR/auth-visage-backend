import base64
import hashlib
import secrets
from datetime import UTC, datetime

from fastapi.routing import APIRoute


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


def generate_auth_code(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def sha256_base64url_encode(input_str: str) -> str:
    """SHA-256 hash a string and encode it in Base64URL (without padding)."""
    sha256_hash = hashlib.sha256(input_str.encode()).digest()
    base64url_encoded = base64.urlsafe_b64encode(sha256_hash).rstrip(b"=")
    return base64url_encoded.decode()


def utcnow() -> datetime:
    return datetime.now(UTC)
