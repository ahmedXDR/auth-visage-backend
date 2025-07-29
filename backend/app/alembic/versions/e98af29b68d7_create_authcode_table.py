"""create authcode table

Revision ID: e98af29b68d7
Revises: 75b3b8c261c1
Create Date: 2025-03-19 23:25:41.402671

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e98af29b68d7"
down_revision: str | None = "75b3b8c261c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "authcode",
        sa.Column(
            "code",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "code_challenge",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["auth.users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("authcode")
