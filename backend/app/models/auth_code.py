import datetime
import uuid

from sqlmodel import Field, SQLModel

from app.models.base import InDBBase


# Shared properties
class AuthCodeBase(SQLModel):
    code: str
    code_challenge: str
    project_id: uuid.UUID


# Properties to receive on project creation
class AuthCodeCreate(AuthCodeBase):
    pass


class AuthCodeUpdate(SQLModel):
    pass


# Database model, database table inferred from class name
class AuthCode(InDBBase, AuthCodeBase, table=True):
    __tablename__ = "auth_code"
    __table_args__ = {"schema": "oauth"}
    owner_id: uuid.UUID = Field(
        foreign_key="auth.users.id",
        nullable=False,
        ondelete="CASCADE",
    )
    project_id: uuid.UUID = Field(
        foreign_key="project.id",
        nullable=False,
        ondelete="CASCADE",
    )


# Properties to return via API, id is always required
class AuthCodePublic(AuthCodeBase):
    id: uuid.UUID
    created_at: datetime.datetime
    owner_id: uuid.UUID


class AuthCodesPublic(SQLModel):
    data: list[AuthCodePublic]
    count: int
