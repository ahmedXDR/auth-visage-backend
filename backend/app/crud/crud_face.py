import uuid

from sqlmodel import Session, text

from app.crud.base import CRUDBase
from app.models.face import Face, FaceCreate, FaceMatch, FaceUpdate


class CRUDFace(CRUDBase[Face, FaceCreate, FaceUpdate]):
    def create(
        self, session: Session, *, owner_id: uuid.UUID, obj_in: FaceCreate
    ) -> Face:
        return super().create(session, owner_id=owner_id, obj_in=obj_in)

    def update(
        self, session: Session, *, id: uuid.UUID, obj_in: FaceUpdate
    ) -> Face | None:
        return super().update(session, id=id, obj_in=obj_in)

    def face_match(
        self, session: Session, *, embedding: list[float], threshold: float
    ) -> FaceMatch | None:
        statement = text(f"""
select *
from (
    select f.owner_id, f.embedding <-> '{str(embedding)}' as distance
    from face f
) a
where distance < {threshold}
order by distance asc
limit 1
""")
        result = session.execute(statement).first()  # type: ignore

        if result is None:
            return None

        return FaceMatch(owner_id=result[0], distance=result[1])


face = CRUDFace(Face)
