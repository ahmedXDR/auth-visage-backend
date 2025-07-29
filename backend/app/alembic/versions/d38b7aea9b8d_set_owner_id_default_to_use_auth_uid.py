"""set owner_id default to use auth.uid()

Revision ID: d38b7aea9b8d
Revises: be7b7d70218e
Create Date: 2025-05-06 23:41:48.741038

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d38b7aea9b8d"
down_revision: str | None = "be7b7d70218e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "project",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=sa.text("auth.uid()"),
    )
    op.alter_column(
        "trusted_origin",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=sa.text("auth.uid()"),
    )
    op.alter_column(
        "user_project_link",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=sa.text("auth.uid()"),
    )
    op.alter_column(
        "face",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=sa.text("auth.uid()"),
    )
    op.alter_column(
        "auth_code",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=sa.text("auth.uid()"),
        schema="oauth",
    )
    op.alter_column(
        "oauth_refresh_token",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=sa.text("auth.uid()"),
        schema="oauth",
    )


def downgrade() -> None:
    op.alter_column(
        "project",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "trusted_origin",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "user_project_link",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "face",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "auth_code",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=None,
        schema="oauth",
    )
    op.alter_column(
        "oauth_refresh_token",
        "owner_id",
        existing_type=sa.UUID(),
        nullable=False,
        server_default=None,
        schema="oauth",
    )
