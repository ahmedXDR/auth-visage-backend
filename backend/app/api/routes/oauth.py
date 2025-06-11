from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Cookie, HTTPException, Request, Response

from app.api.deps import SessionDep
from app.core.db import generate_oauth_token, refresh_oauth_token
from app.crud import (
    auth_code,
    oauth_refresh_token,
    oauth_session,
    project,
    trusted_origin,
)
from app.models.oauth_session import OAuthSession, OAuthSessionCreate
from app.schemas import OAuthTokenRequest
from app.utils import sha256_base64url_encode

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.post(
    "/create-session",
)
async def create_session(
    request: Request,
    oauth_session_in: OAuthSessionCreate,
    session: SessionDep,
) -> OAuthSession:
    # check if project exists
    project_obj = project.get(session, id=oauth_session_in.project_id)
    if project_obj is None:
        raise HTTPException(status_code=400, detail="Invalid project id")

    request_origin = request.headers.get("origin")
    if request_origin is None:
        raise HTTPException(status_code=400, detail="Missing origin header")
    trusted_origin_obj = trusted_origin.get_by_name_and_project(
        session,
        name=request_origin,
        project_id=oauth_session_in.project_id,
    )
    if trusted_origin_obj is None:
        raise HTTPException(status_code=400, detail="Invalid origin")

    oauth_session_obj = oauth_session.create(session, obj_in=oauth_session_in)

    return oauth_session_obj


@router.post(
    "/token",
)
async def get_token(
    response: Response,
    token_request: OAuthTokenRequest,
    session: SessionDep,
) -> dict[str, str]:
    code = token_request.code
    code_obj = auth_code.get_by_code(session, code=code)

    if code_obj is None:
        raise HTTPException(status_code=400, detail="Invalid code")

    created_at = code_obj.created_at
    if created_at < datetime.now(UTC) - timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="Code expired")

    code_verifier = token_request.code_verifier

    verifier_hash = sha256_base64url_encode(code_verifier)
    code_challenge = code_obj.code_challenge

    if verifier_hash != code_challenge:
        raise HTTPException(status_code=400, detail="Invalid code verifier")

    # delete the code
    auth_code.remove(session, id=code_obj.id)

    oauth_token = generate_oauth_token(
        session,
        code_obj.owner_id,
        code_obj.project_id,
    )

    # Set tokens as HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=oauth_token.access_token,
        max_age=oauth_token.expires_in,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=oauth_token.refresh_token,
        max_age=30 * 24 * 60 * 60,  # 30 days
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"message": "Tokens set successfully"}


@router.post(
    "/refresh-token",
)
async def refresh_token(
    response: Response,
    session: SessionDep,
    refresh_token: str = Cookie(None),
) -> dict[str, str]:
    if refresh_token is None:
        raise HTTPException(
            status_code=400,
            detail="Missing refresh_token cookie",
        )

    refresh_token_obj = oauth_refresh_token.get_by_token(
        session, token=refresh_token
    )
    if refresh_token_obj is None:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    oauth_session_obj = oauth_session.get(
        session, id=refresh_token_obj.oauth_session_id
    )

    oauth_token = refresh_oauth_token(
        session,
        refresh_token_obj,
        oauth_session_obj,
    )

    # Set tokens as HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=oauth_token.access_token,
        max_age=oauth_token.expires_in,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=oauth_token.refresh_token,
        max_age=30 * 24 * 60 * 60,  # 30 days
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"message": "Tokens refreshed successfully"}
