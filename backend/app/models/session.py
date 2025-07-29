from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import TIMESTAMP, Field, SQLModel

from app.utils import utcnow


class AALLevel(str, Enum):
    aal1 = "aal1"
    aal2 = "aal2"
    aal3 = "aal3"


class Session(SQLModel, table=True):
    """NOTE: do not migrate with alembic with it"""

    __tablename__ = "sessions"
    __table_args__ = {"schema": "auth", "keep_existing": True}
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    aal: AALLevel = Field(default=AALLevel.aal1)
    user_id: UUID
    factor_id: UUID | None = None
    created_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),
    )  # type: ignore
    updated_at: datetime | None = Field(
        default_factory=utcnow,
        nullable=False,
        sa_column_kwargs={
            "onupdate": utcnow,
        },
        sa_type=TIMESTAMP(timezone=True),
    )  # type: ignore


def new_session(user_id: UUID, factor_id: UUID | None = None) -> Session:
    return Session(
        id=uuid4(),
        aal=AALLevel.aal1,
        user_id=user_id,
        factor_id=factor_id,
    )
