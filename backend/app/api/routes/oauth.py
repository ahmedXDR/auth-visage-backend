from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Request

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
from app.schemas import OAuthToken, OAuthTokenRequest
from app.utils import sha256_base64url_encode

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get(
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

    trusted_origin_obj = trusted_origin.get_by_name(
        session,
        name=request_origin,
    )
    if trusted_origin_obj is None:
        raise HTTPException(status_code=400, detail="Invalid origin")

    oauth_session_obj = oauth_session.create(session, obj_in=oauth_session_in)

    return oauth_session_obj


@router.post(
    "/token",
    response_model=OAuthToken,
)
async def get_token(
    token_request: OAuthTokenRequest,
    session: SessionDep,
) -> OAuthToken:
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

    return generate_oauth_token(
        session,
        code_obj.owner_id,
        code_obj.project_id,
    )


@router.post(
    "/refresh-token",
    response_model=OAuthToken,
)
async def refresh_token(
    refresh_token: str,
    session: SessionDep,
) -> OAuthToken:
    refresh_token_obj = oauth_refresh_token.get_by_token(
        session, token=refresh_token
    )
    if refresh_token_obj is None:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    oauth_session_obj = oauth_session.get(
        session, id=refresh_token_obj.oauth_session_id
    )
    if oauth_session_obj is None:
        raise HTTPException(status_code=400, detail="Session expired")

    return refresh_oauth_token(
        session,
        refresh_token_obj,
        oauth_session_obj,
    )
