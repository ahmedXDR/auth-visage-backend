"""create face table

Revision ID: 4af69e22476a
Revises: e98af29b68d7
Create Date: 2025-04-09 13:24:57.960179

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector  # type: ignore

# revision identifiers, used by Alembic.
revision: str = "4af69e22476a"
down_revision: str | None = "e98af29b68d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        "face",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "embedding",
            Vector(128),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["auth.users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute("CREATE INDEX ON face USING hnsw (embedding vector_l2_ops)")


def downgrade() -> None:
    op.drop_table("face")
    op.execute("DROP EXTENSION IF EXISTS vector;")
    op.execute("DROP INDEX ON face USING hnsw")
