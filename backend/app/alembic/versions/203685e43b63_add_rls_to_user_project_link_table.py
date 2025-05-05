"""add rls to user_project_link table

Revision ID: 203685e43b63
Revises: a6238d3693bd
Create Date: 2025-05-05 20:36:04.967862

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "203685e43b63"
down_revision: str | None = "a6238d3693bd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE user_project_link ENABLE ROW LEVEL SECURITY")

    op.execute("""
        CREATE POLICY "Enable users to handle their own data only"
        ON "public"."user_project_link"
        AS PERMISSIVE
        FOR ALL
        TO authenticated
        USING ((SELECT auth.uid()) = owner_id)
    """)


def downgrade() -> None:
    op.execute(
        'DROP POLICY IF EXISTS "Enable users to handle their own data only" ON "public"."user_project_link"'
    )
    op.execute("ALTER TABLE user_project_link DISABLE ROW LEVEL SECURITY")
