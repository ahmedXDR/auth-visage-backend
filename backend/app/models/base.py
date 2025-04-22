import uuid
from datetime import datetime

from sqlmodel import TIMESTAMP, Field, SQLModel

from app.utils import utcnow


class InDBBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),
    )  # type: ignore
