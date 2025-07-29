"""auto generate uuids in db

Revision ID: a6e4e460511c
Revises: 2f48b943bcd6
Create Date: 2025-05-18 14:09:47.091877

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a6e4e460511c"
down_revision: str | None = "2f48b943bcd6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        table_name="project",
        column_name="id",
        server_default=sa.text("gen_random_uuid()"),
    )
    op.alter_column(
        table_name="face",
        column_name="id",
        server_default=sa.text("gen_random_uuid()"),
    )
    op.alter_column(
        table_name="trusted_origin",
        column_name="id",
        server_default=sa.text("gen_random_uuid()"),
    )
    op.alter_column(
        table_name="auth_code",
        column_name="id",
        server_default=sa.text("gen_random_uuid()"),
        schema="oauth",
    )
    op.alter_column(
        table_name="oauth_refresh_token",
        column_name="id",
        server_default=sa.text("gen_random_uuid()"),
        schema="oauth",
    )
    op.alter_column(
        table_name="oauth_session",
        column_name="id",
        server_default=sa.text("gen_random_uuid()"),
        schema="oauth",
    )


def downgrade() -> None:
    op.alter_column(
        table_name="project",
        column_name="id",
        server_default=None,
    )
    op.alter_column(
        table_name="face",
        column_name="id",
        server_default=None,
    )
    op.alter_column(
        table_name="trusted_origin",
        column_name="id",
        server_default=None,
    )
    op.alter_column(
        table_name="auth_code",
        column_name="id",
        server_default=None,
        schema="oauth",
    )
    op.alter_column(
        table_name="oauth_refresh_token",
        column_name="id",
        server_default=None,
        schema="oauth",
    )
    op.alter_column(
        table_name="oauth_session",
        column_name="id",
        server_default=None,
        schema="oauth",
    )
