"""add rls to backend only tables

Revision ID: be7b7d70218e
Revises: 203685e43b63
Create Date: 2025-05-05 20:43:01.986874

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "be7b7d70218e"
down_revision: str | None = "203685e43b63"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Public tables
    op.execute("ALTER TABLE alembic_version ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE face ENABLE ROW LEVEL SECURITY")

    # Oauth tables
    op.execute("ALTER TABLE oauth.oauth_session ENABLE ROW LEVEL SECURITY")
    op.execute(
        "ALTER TABLE oauth.oauth_refresh_token ENABLE ROW LEVEL SECURITY"
    )
    op.execute("ALTER TABLE oauth.auth_code ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.execute("ALTER TABLE alembic_version DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE face DISABLE ROW LEVEL SECURITY")

    op.execute("ALTER TABLE oauth.oauth_session DISABLE ROW LEVEL SECURITY")
    op.execute(
        "ALTER TABLE oauth.oauth_refresh_token DISABLE ROW LEVEL SECURITY"
    )
    op.execute("ALTER TABLE oauth.auth_code DISABLE ROW LEVEL SECURITY")
