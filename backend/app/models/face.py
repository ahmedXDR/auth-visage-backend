import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector  # type: ignore
from sqlmodel import Field, SQLModel

from app.models.base import InDBBase


# Shared properties
class FaceBase(SQLModel):
    embedding: list[float]


# Properties to receive on face creation
class FaceCreate(FaceBase):
    pass


# Properties to receive on face update
class FaceUpdate(SQLModel):
    embedding: list[float] | None = None


# Data base model, database table inferred from class name
class Face(InDBBase, FaceBase, table=True):
    embedding: Any = Field(sa_type=Vector(128))


class FaceMatch(SQLModel):
    owner_id: uuid.UUID
    distance: float


# Properties to return via API, id is always required
class FacePublic(FaceBase):
    id: uuid.UUID
    created_at: datetime
    owner_id: uuid.UUID


class FacesPublic(SQLModel):
    data: list[FacePublic]
    count: int
