"""add face orientations

Revision ID: c9e60285f45e
Revises: 341cf6806d6f
Create Date: 2025-05-23 20:03:52.067382

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector  # type: ignore

# revision identifiers, used by Alembic.
revision: str = "c9e60285f45e"
down_revision: str | None = "341cf6806d6f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "face",
        sa.Column(
            "center_embedding",
            Vector(dim=128),
            nullable=False,
        ),
    )
    op.add_column(
        "face",
        sa.Column(
            "left_embedding",
            Vector(dim=128),
            nullable=True,
        ),
    )
    op.add_column(
        "face",
        sa.Column(
            "right_embedding",
            Vector(dim=128),
            nullable=True,
        ),
    )
    op.drop_column("face", "embedding")


def downgrade() -> None:
    op.add_column(
        "face",
        sa.Column(
            "embedding",
            Vector(dim=128),
            nullable=False,
        ),
    )
    op.drop_column("face", "right_embedding")
    op.drop_column("face", "left_embedding")
    op.drop_column("face", "center_embedding")
