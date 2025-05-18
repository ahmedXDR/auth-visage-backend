"""auto generate timestamps in db

Revision ID: 33e5105ab73d
Revises: a6e4e460511c
Create Date: 2025-05-18 14:30:41.902208

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "33e5105ab73d"
down_revision: str | None = "a6e4e460511c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        table_name="project",
        column_name="created_at",
        server_default=sa.text("timezone('utc', now())"),
    )
    op.alter_column(
        table_name="face",
        column_name="created_at",
        server_default=sa.text("timezone('utc', now())"),
    )
    op.alter_column(
        table_name="trusted_origin",
        column_name="created_at",
        server_default=sa.text("timezone('utc', now())"),
    )
    op.alter_column(
        table_name="user_project_link",
        column_name="created_at",
        server_default=sa.text("timezone('utc', now())"),
    )
    op.alter_column(
        table_name="auth_code",
        column_name="created_at",
        server_default=sa.text("timezone('utc', now())"),
        schema="oauth",
    )
    op.alter_column(
        table_name="oauth_refresh_token",
        column_name="created_at",
        server_default=sa.text("timezone('utc', now())"),
        schema="oauth",
    )
    op.alter_column(
        table_name="oauth_session",
        column_name="created_at",
        server_default=sa.text("timezone('utc', now())"),
        schema="oauth",
    )


def downgrade() -> None:
    op.alter_column(
        table_name="project",
        column_name="created_at",
        server_default=None,
    )
    op.alter_column(
        table_name="face",
        column_name="created_at",
        server_default=None,
    )
    op.alter_column(
        table_name="trusted_origin",
        column_name="created_at",
        server_default=None,
    )
    op.alter_column(
        table_name="user_project_link",
        column_name="created_at",
        server_default=None,
    )
    op.alter_column(
        table_name="auth_code",
        schema="oauth",
        column_name="created_at",
        server_default=None,
    )
    op.alter_column(
        table_name="oauth_refresh_token",
        schema="oauth",
        column_name="created_at",
        server_default=None,
    )
    op.alter_column(
        table_name="oauth_session",
        schema="oauth",
        column_name="created_at",
        server_default=None,
    )
