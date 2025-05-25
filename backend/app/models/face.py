import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pgvector.sqlalchemy import Vector  # type: ignore
from sqlmodel import Field, SQLModel

from app.models.base import InDBBase


# Shared properties
class FaceBase(SQLModel):
    center_embedding: list[float]
    left_embedding: list[float] | None = None
    right_embedding: list[float] | None = None


# Properties to receive on face creation
class FaceCreate(FaceBase):
    pass


# Properties to receive on face update
class FaceUpdate(SQLModel):
    center_embedding: list[float] | None = None
    left_embedding: list[float] | None = None
    right_embedding: list[float] | None = None


# Data base model, database table inferred from class name
class Face(InDBBase, FaceBase, table=True):
    center_embedding: Any = Field(sa_type=Vector(128))
    left_embedding: Any = Field(
        sa_type=Vector(128),
        default=None,
        nullable=True,
    )
    right_embedding: Any = Field(
        sa_type=Vector(128),
        default=None,
        nullable=True,
    )
    owner_id: uuid.UUID = Field(
        foreign_key="auth.users.id",
        nullable=False,
        ondelete="CASCADE",
    )


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


class FaceOrientation(str, Enum):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
