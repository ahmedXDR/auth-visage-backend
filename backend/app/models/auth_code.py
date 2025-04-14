import datetime
import uuid

from sqlmodel import SQLModel

from app.models.base import InDBBase


# Shared properties
class AuthCodeBase(SQLModel):
    code: str
    code_challenge: str


# Properties to receive on project creation
class AuthCodeCreate(AuthCodeBase):
    pass


# Database model, database table inferred from class name
class AuthCode(InDBBase, AuthCodeBase, table=True):
    pass


# Properties to return via API, id is always required
class AuthCodePublic(AuthCodeBase):
    id: uuid.UUID
    created_at: datetime.datetime
    owner_id: uuid.UUID


class AuthCodesPublic(SQLModel):
    data: list[AuthCodePublic]
    count: int
