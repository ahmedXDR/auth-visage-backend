"""add rls to trusted_origin table

Revision ID: a6238d3693bd
Revises: 19e4fcf54e48
Create Date: 2025-05-05 20:14:53.623330

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a6238d3693bd"
down_revision: str | None = "19e4fcf54e48"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE trusted_origin ENABLE ROW LEVEL SECURITY")

    op.execute("""
        CREATE POLICY "Enable users to handle their own data only"
        ON "public"."trusted_origin"
        AS PERMISSIVE
        FOR ALL
        TO authenticated
        USING ((SELECT auth.uid()) = owner_id)
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM project
                WHERE project.id = trusted_origin.project_id
                AND project.owner_id = (SELECT auth.uid())
            )
        )
    """)


def downgrade() -> None:
    op.execute(
        'DROP POLICY IF EXISTS "Enable users to handle their own data only" ON "public"."trusted_origin"'
    )
    op.execute("ALTER TABLE trusted_origin DISABLE ROW LEVEL SECURITY")
