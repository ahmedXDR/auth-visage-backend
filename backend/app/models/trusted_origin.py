from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import InDBBase


# Shared properties
class TrustedOriginBase(SQLModel):
    name: str
    project_id: UUID


# Properties to receive on project creation
class TrustedOriginCreate(TrustedOriginBase):
    pass


# Properties to receive on project update
class TrustedOriginUpdate(SQLModel):
    name: str | None
    project_id: UUID | None


# Database model, database table inferred from class name
class TrustedOrigin(InDBBase, TrustedOriginBase, table=True):
    __tablename__ = "trusted_origin"
    project_id: UUID = Field(
        foreign_key="project.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner_id: UUID = Field(
        foreign_key="auth.users.id",
        nullable=False,
        ondelete="CASCADE",
    )


# Properties to return via API, id is always required
class TrustedOriginPublic(TrustedOriginBase):
    id: UUID
    created_at: datetime
    owner_id: UUID


class TrustedOriginsPublic(SQLModel):
    data: list[TrustedOriginPublic]
    count: int
