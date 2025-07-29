from datetime import datetime
from uuid import UUID

from sqlmodel import TIMESTAMP, Field, SQLModel

from app.models.base import InDBBase


class OAuthSessionBase(SQLModel):
    project_id: UUID


class OAuthSessionCreate(OAuthSessionBase):
    pass


class OAuthSessionUpdate(SQLModel):
    project_id: UUID | None
    refreshed_at: datetime | None


class OAuthSession(InDBBase, OAuthSessionBase, table=True):
    __tablename__ = "oauth_session"
    __table_args__ = {"schema": "oauth"}
    refreshed_at: datetime | None = Field(
        default_factory=None,
        sa_type=TIMESTAMP(timezone=True),
    )  # type: ignore


class OAuthSessionPublic(OAuthSessionBase):
    id: UUID
    created_at: datetime
    refreshed_at: datetime | None


class OAuthSessionsPublic(SQLModel):
    data: list[OAuthSessionPublic]
    count: int
