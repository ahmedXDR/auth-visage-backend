import base64
import datetime
import os
from typing import Any

import jwt
from fastapi import HTTPException

from app.core.auth import get_super_client
from app.core.config import settings


def secure_token() -> str:
    """Generate a secure random token."""
    b = os.urandom(16)
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def create_jwt_token(user_data: dict[str, Any]) -> str:
    """Create and sign a JWT token for the user."""
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


def get_user_data(user_id: str) -> dict[str, Any]:
    """Get user session from Supabase."""
    super_client = get_super_client()
    user = super_client.auth.admin.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data: dict[str, Any] = user.user.model_dump()
    return user_data
