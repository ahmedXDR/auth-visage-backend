from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from supabase_auth import User, UserAttributes  # type: ignore


class RefreshToken(BaseModel):
    instance_id: UUID | None = None
    id: int | None = None
    token: str
    user_id: UUID
    session_id: UUID | None = None
    revoked: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Session(BaseModel):
    id: UUID
    aal: str
    user_id: UUID
    factor_id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# Shared properties
class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None


class TokenRequest(BaseModel):
    code: str
    code_verifier: str


# request
class UserIn(Token, User):  # type: ignore
    pass


# Properties to receive via API on creation
# in
class UserCreate(BaseModel):
    pass


# Properties to receive via API on update
# in
class UserUpdate(UserAttributes):  # type: ignore
    pass


# response


class UserInDBBase(BaseModel):
    pass


# Properties to return to client via api
# out
class UserOut(Token):
    pass


# Properties properties stored in DB
class UserInDB(User):  # type: ignore
    pass
