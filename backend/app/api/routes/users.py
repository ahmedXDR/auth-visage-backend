import logging

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.core.auth import SuperClient

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger("uvicorn")


@router.get("/me")
async def get_me(
    current_user: CurrentUser,
) -> dict[str, str]:
    """
    Get the current user's information.

    This endpoint returns the details of the authenticated user.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
    }


@router.delete("/me")
async def delete_me(
    current_user: CurrentUser,
    super_client: SuperClient,
) -> dict[str, str]:
    """
    Delete the current user's account.

    This endpoint allows authenticated users to delete their own account
    using Supabase's admin delete user functionality.
    """
    await super_client.auth.admin.delete_user(current_user.id)
    logger.info(f"Successfully deleted user {current_user.id}")

    return {"message": "User account deleted successfully"}
