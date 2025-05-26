from enum import Enum
from random import choice
from uuid import UUID

from PIL import Image
from pydantic import BaseModel, ConfigDict
from supabase_auth import User, UserAttributes

from app.models.face import FaceCreate, FaceOrientation


# Shared properties
class OAuthToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class OAuthTokenRequest(BaseModel):
    code: str
    code_verifier: str


class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None


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


class AuthTypes(str, Enum):
    """Authentication types supported by the WebSocket interface."""

    OAUTH = "oauth"
    LOGIN = "login"
    REGISTER = "register"


class SioUserSession(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str | None = None
    origin: str | None = None
    pending_oauth: bool = False
    auth_type: AuthTypes | None = None
    code_challenge: str | None = None
    oauth_session_uuid: UUID | None = None
    liveness_frames: list[Image.Image] = []
    face_data: FaceCreate | None = None
    random_orientation: FaceOrientation = choice(list(FaceOrientation))
