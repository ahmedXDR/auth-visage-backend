from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.core.db import generate_user_session
from app.crud import auth_code
from app.schemas import Token, TokenRequest
from app.utils import sha256_base64url_encode

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.post(
    "/token",
    response_model=Token,
)
async def get_token(
    token_request: TokenRequest,
    session: SessionDep,
) -> Token:
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

    return await generate_user_session(code_obj.owner_id)
