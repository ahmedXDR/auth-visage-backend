from datetime import datetime
from secrets import token_urlsafe
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import InDBBase


class OAuthRefreshTokenBase(SQLModel):
    token: str = Field(
        default_factory=lambda: token_urlsafe(16),
        max_length=255,
        unique=True,
    )
    oauth_session_id: UUID
    revoked: bool = False


class OAuthRefreshTokenCreate(OAuthRefreshTokenBase):
    pass


class OAuthRefreshTokenUpdate(SQLModel):
    pass


class OAuthRefreshToken(InDBBase, OAuthRefreshTokenBase, table=True):
    __tablename__ = "oauth_refresh_token"
    __table_args__ = {"schema": "oauth"}
    oauth_session_id: UUID = Field(
        foreign_key="oauth.oauth_session.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner_id: UUID = Field(
        foreign_key="auth.users.id",
        nullable=False,
        ondelete="CASCADE",
    )


class OAuthRefreshTokenPublic(OAuthRefreshTokenBase):
    id: UUID
    created_at: datetime
    revoked: bool
    owner_id: UUID


class OAuthRefreshTokensPublic(SQLModel):
    data: list[OAuthRefreshTokenPublic]
    count: int
