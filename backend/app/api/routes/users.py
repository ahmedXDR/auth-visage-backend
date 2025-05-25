import logging

from fastapi import APIRouter, HTTPException
from supabase import AuthError

from app.api.deps import CurrentUser
from app.core.auth import SuperClient

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger("uvicorn")


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
    try:
        await super_client.auth.admin.delete_user(current_user.id)
        logger.info(f"Successfully deleted user {current_user.id}")
        return {"message": "User account deleted successfully"}

    except AuthError as e:
        logger.error(f"Auth error while deleting user {current_user.id}: {e}")
        raise HTTPException(
            status_code=400, detail=f"Authentication error: {e}"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error while deleting user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while deleting the account",
        )
