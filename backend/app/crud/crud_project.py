from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.project import Project, ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def create(
        self,
        session: Session,
        *,
        obj_in: ProjectCreate,
        owner_id: UUID | None = None,
    ) -> Project:
        if owner_id is None:
            raise ValueError("owner_id is required")

        return super().create(session, obj_in=obj_in, owner_id=owner_id)

    def get_multi_by_owner(
        self,
        session: Session,
        *,
        owner_id: UUID,
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
