from datetime import datetime
from uuid import UUID

from sqlmodel import TIMESTAMP, Field, SQLModel, text

from app.utils import utcnow


# Shared properties
class UserProjectLinkBase(SQLModel):
    project_id: UUID


# Properties to receive on project creation
class UserProjectLinkCreate(UserProjectLinkBase):
    pass


# Properties to receive on project update
class UserProjectLinkUpdate(UserProjectLinkBase):
    last_sign_in: datetime | None


# Database model, database table inferred from class name
class UserProjectLink(UserProjectLinkBase, table=True):
    __tablename__ = "user_project_link"
    project_id: UUID = Field(
        primary_key=True,
        foreign_key="project.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner_id: UUID = Field(
        primary_key=True,
        foreign_key="auth.users.id",
        nullable=False,
        ondelete="CASCADE",
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),
        sa_column_kwargs={
            "server_default": text("timezone('utc', now())"),
        },
    )  # type: ignore
    last_sign_in: datetime | None = Field(
        default_factory=None,
        sa_type=TIMESTAMP(timezone=True),
    )  # type: ignore


# Properties to return via API, id is always required
class UserProjectLinkPublic(UserProjectLinkBase):
    project_id: UUID
    owner_id: UUID
    created_at: datetime
    last_sign_in: datetime | None


class UserProjectLinksPublic(SQLModel):
    data: list[UserProjectLinkPublic]
    count: int
