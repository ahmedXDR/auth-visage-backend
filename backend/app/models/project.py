import datetime
import uuid

from sqlmodel import Field, SQLModel

from app.models.base import InDBBase


# Shared properties
class ProjectBase(SQLModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=2048,
    )
    logo_url: str | None = Field(
        default=None,
        min_length=1,
        max_length=2048,
    )


# Properties to receive on project creation
class ProjectCreate(ProjectBase):
    pass


# Properties to receive on project update
class ProjectUpdate(SQLModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=2048,
    )
    logo_url: str | None = Field(
        default=None,
        min_length=1,
        max_length=2048,
    )


# Database model, database table inferred from class name
class Project(InDBBase, ProjectBase, table=True):
    owner_id: uuid.UUID = Field(
        foreign_key="auth.users.id",
        nullable=False,
        ondelete="CASCADE",
    )


# Properties to return via API, id is always required
class ProjectPublic(ProjectBase):
    id: uuid.UUID
    api_key: str
    model_usage: int
    created_at: datetime.datetime
    owner_id: uuid.UUID


class ProjectsPublic(SQLModel):
    data: list[ProjectPublic]
    count: int
