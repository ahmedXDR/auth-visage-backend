"""add rls to face table

Revision ID: 341cf6806d6f
Revises: 33e5105ab73d
Create Date: 2025-05-18 21:30:17.400761

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "341cf6806d6f"
down_revision: str | None = "33e5105ab73d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        create policy "Enable delete for users based on owner_id" on "public"."face" as PERMISSIVE for delete to authenticated using (
        (
            select
            auth.uid ()
        ) = owner_id
        )
    """)


def downgrade() -> None:
    op.execute(
        'drop policy IF exists "Enable delete for users based on owner_id" on "public"."face"'
    )
