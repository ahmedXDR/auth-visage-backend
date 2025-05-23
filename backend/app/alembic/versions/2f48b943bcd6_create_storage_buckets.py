"""create storage buckets

Revision ID: 2f48b943bcd6
Revises: d38b7aea9b8d
Create Date: 2025-05-18 13:10:57.034708

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f48b943bcd6"
down_revision: str | None = "d38b7aea9b8d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        insert into storage.buckets
            (id, name, public)
        values
            ('avatars', 'avatars', true)
    """)
    op.execute("""
        insert into storage.buckets
            (id, name, public)
        values
            ('projects', 'projects', true)
    """)

    op.execute("""
        create policy "Give users access to own avatars' folder" on storage.objects for all to using (
        bucket_id = 'avatars'
        and (
            select
            auth.uid ()::text
        ) = (storage.foldername (name)) [1]
        )
        with
        check (
            bucket_id = 'avatars'
            and (
            select
                auth.uid ()::text
            ) = (storage.foldername (name)) [1]
        )
    """)
    op.execute("""
        create policy "Give users access to own projects' folder" on storage.objects for all to public using (
        bucket_id = 'projects'
        and (
            select
            auth.uid ()::text
        ) = (storage.foldername (name)) [1]
        )
        with
        check (
            bucket_id = 'projects'
            and (
            select
                auth.uid ()::text
            ) = (storage.foldername (name)) [1]
        )
    """)


def downgrade() -> None:
    op.execute("""
        delete from storage.buckets
        where id = 'avatars'
    """)
    op.execute("""
        delete from storage.buckets
        where id = 'projects'
    """)
    op.execute(
        """drop policy IF exists "Give users access to own projects' folder" on storage.objects"""
    )
    op.execute(
        """drop policy IF exists "Give users access to own avatars' folder" on storage.objects"""
    )
