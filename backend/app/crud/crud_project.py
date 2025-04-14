import uuid

from sqlmodel import Session

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


project = CRUDProject(Project)
