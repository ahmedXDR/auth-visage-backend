"""create user_project_link_table

Revision ID: 0ae3bdc1f5e8
Revises: 1aa1b824b5ae
Create Date: 2025-04-22 19:27:50.006405

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0ae3bdc1f5e8"
down_revision: str | None = "1aa1b824b5ae"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_project_link",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("last_sign_in", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["auth.users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["project.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("project_id", "owner_id"),
    )


def downgrade() -> None:
    op.drop_table("user_project_link")
