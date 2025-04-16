import uuid
from collections.abc import Sequence

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.project import Project, ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def create(
        self, session: Session, *, owner_id: uuid.UUID, obj_in: ProjectCreate
    ) -> Project:
        return super().create(session, owner_id=owner_id, obj_in=obj_in)

    def update(
        self, session: Session, *, id: uuid.UUID, obj_in: ProjectUpdate
    ) -> Project | None:
        return super().update(session, id=id, obj_in=obj_in)

    def get_multi_by_owner(
        self,
        session: Session,
        *,
        owner_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Project]:
        statement = (
            select(self.model)
            .where(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        result = session.exec(statement)
        return result.all()


project = CRUDProject(Project)
