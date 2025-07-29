"""add rls to project table

Revision ID: 19e4fcf54e48
Revises: 0ae3bdc1f5e8
Create Date: 2025-05-05 20:07:33.834528

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "19e4fcf54e48"
down_revision: str | None = "0ae3bdc1f5e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Enable RLS on the project table
    op.execute("ALTER TABLE project ENABLE ROW LEVEL SECURITY")

    # Create a single comprehensive policy for all operations
    op.execute("""
        CREATE POLICY "Enable users to handle their own data only"
        ON "public"."project"
        AS PERMISSIVE
        FOR ALL
        TO authenticated
        USING ((SELECT auth.uid()) = owner_id)
    """)


def downgrade() -> None:
    # Drop policy
    op.execute(
        'DROP POLICY IF EXISTS "Enable users to handle their own data only" ON "public"."project"'
    )

    # Disable RLS
    op.execute("ALTER TABLE project DISABLE ROW LEVEL SECURITY")
