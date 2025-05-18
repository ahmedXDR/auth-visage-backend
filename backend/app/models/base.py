import uuid
from datetime import datetime

from sqlmodel import TIMESTAMP, Field, SQLModel, text

from app.utils import utcnow


class InDBBase(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
        },
    )

    created_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),
        sa_column_kwargs={
            "server_default": text("timezone('utc', now())"),
        },
    )  # type: ignore
