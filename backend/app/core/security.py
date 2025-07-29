import datetime
from typing import Any
from uuid import UUID

import jwt
from supabase import AuthError

from app.core.auth import get_super_client
from app.core.config import settings


def create_jwt_token(user_data: dict[str, Any]) -> str:
    """Create and sign a JWT token for the user."""
    jwt_data = {
        "sub": user_data["id"],
        "exp": datetime.datetime.now(datetime.UTC)
        + datetime.timedelta(seconds=settings.JWT_lifespan),
        "email": user_data.get("email", ""),
    }

    return jwt.encode(
        jwt_data,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_supabase_jwt_token(user_data: dict[str, Any]) -> str:
    """Create and sign a Supabase JWT token for the user."""
    jwt_data = {
        "sub": user_data["id"],
        "aud": "authenticated",
        "exp": datetime.datetime.now(datetime.UTC)
        + datetime.timedelta(seconds=settings.JWT_lifespan),
        "email": user_data.get("email", ""),
        "role": "authenticated",
        "aal": "aal1",
    }

    return jwt.encode(
        jwt_data,
        settings.SUPABASE_JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def get_user_data(user_id: str | UUID) -> dict[str, Any] | None:
    """Get user session from Supabase."""
    super_client = get_super_client()
    try:
        user = super_client.auth.admin.get_user_by_id(str(user_id))
    except AuthError:
        return None

    user_data: dict[str, Any] = user.user.model_dump()
    return user_data
