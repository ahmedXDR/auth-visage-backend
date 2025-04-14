import uuid

from sqlmodel import Session

from app.crud.base import CRUDBase
from app.models.face import Face, FaceCreate, FaceUpdate


class CRUDFace(CRUDBase[Face, FaceCreate, FaceUpdate]):
    def create(
        self, session: Session, *, owner_id: uuid.UUID, obj_in: FaceCreate
    ) -> Face:
        return super().create(session, owner_id=owner_id, obj_in=obj_in)

    def update(
        self, session: Session, *, id: uuid.UUID, obj_in: FaceUpdate
    ) -> Face | None:
        return super().update(session, id=id, obj_in=obj_in)


face = CRUDFace(Face)
