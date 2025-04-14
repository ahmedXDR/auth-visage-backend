import uuid
from datetime import datetime

from sqlmodel import TIMESTAMP, Field, SQLModel

from app.utils import utcnow


class RefreshToken(SQLModel, table=True):
    """NOTE: do not migrate with alembic with it"""

    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "auth", "keep_existing": True}
    instance_id: uuid.UUID | None = Field(default=None)
    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(max_length=255)
    user_id: uuid.UUID = Field(
        foreign_key="auth.users.id",
        nullable=False,
        ondelete="CASCADE",
    )
    revoked: bool = Field(default=False)
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
    session_id: uuid.UUID | None = Field(default=None)
