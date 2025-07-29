from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session, select

from app.models.user_project_link import (
    UserProjectLink,
    UserProjectLinkCreate,
    UserProjectLinkUpdate,
)


class CRUDUserProjectLink:
    def get(
        self,
        session: Session,
        *,
        owner_id: UUID,
        project_id: UUID,
    ) -> UserProjectLink | None:
        """Get a single record by user_id and project_id"""
        statement = select(UserProjectLink).where(
            UserProjectLink.owner_id == owner_id,
            UserProjectLink.project_id == project_id,
        )
        result = session.exec(statement)
        return result.one_or_none()

    def get_multi(
        self,
        session: Session,
        *,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[UserProjectLink]:
        """Get multiple records for an owner with pagination"""
        statement = (
            select(UserProjectLink)
            .where(UserProjectLink.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        result = session.exec(statement)
        return result.all()

    def create(
        self,
        session: Session,
        *,
        owner_id: UUID,
        obj_in: UserProjectLinkCreate,
    ) -> UserProjectLink:
        """Create new record"""
        db_obj = UserProjectLink(
            **dict(owner_id=owner_id, **obj_in.model_dump())
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        *,
        owner_id: UUID,
        project_id: UUID,
        obj_in: UserProjectLinkUpdate,
    ) -> UserProjectLink | None:
        """Update existing record"""
        db_obj = self.get(session, owner_id=owner_id, project_id=project_id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            db_obj.sqlmodel_update(update_data)

            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj

    def remove(
        self,
        session: Session,
        *,
        owner_id: UUID,
        project_id: UUID,
    ) -> UserProjectLink | None:
        """Remove a record"""
        obj = self.get(session, owner_id=owner_id, project_id=project_id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj


user_project_link = CRUDUserProjectLink()
