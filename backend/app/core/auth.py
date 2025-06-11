import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import (
    AClient,
    AsyncClientOptions,
    Client,
    acreate_client,
    create_client,
)

from app.core.config import settings
from app.schemas.auth import UserIn

logger = logging.getLogger("uvicorn")


def get_super_client() -> Client:
    client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
    )
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Super client not initialized",
        )
    return client


async def get_async_super_client() -> AClient:
    """for validation access_token init at life span event"""
    super_client = await acreate_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
        options=AsyncClientOptions(
            postgrest_client_timeout=10, storage_client_timeout=10
        ),
    )
    if not super_client:
        raise HTTPException(
            status_code=500,
            detail="Super client not initialized",
        )
    return super_client


SuperClient = Annotated[AClient, Depends(get_async_super_client)]

security = HTTPBearer()


async def get_current_user(
    super_client: SuperClient,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> UserIn:
    """get current user from token and validate same time"""
    token = credentials.credentials
    try:
        user_rsp = await super_client.auth.get_user(jwt=token)
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=404, detail="User not found")

    return UserIn(**user_rsp.user.model_dump(), access_token=token)
