from uuid import UUID

from sqlmodel import Session, text

from app.core.config import settings
from app.crud.base import CRUDBase
from app.models.face import (
    Face,
    FaceCreate,
    FaceMatch,
    FaceOrientation,
    FaceUpdate,
)


class CRUDFace(CRUDBase[Face, FaceCreate, FaceUpdate]):
    def create(
        self,
        session: Session,
        *,
        obj_in: FaceCreate,
        owner_id: UUID | None = None,
    ) -> Face:
        if owner_id is None:
            raise ValueError("owner_id is required")

        return super().create(session, obj_in=obj_in, owner_id=owner_id)

    def face_match(
        self,
        session: Session,
        *,
        embedding: list[float],
        face_orientation: FaceOrientation = FaceOrientation.CENTER,
        threshold: float = settings.FACE_MATCH_THRESHOLD,
    ) -> FaceMatch | None:
        statement = text(
            f"""
select *
from (
    select f.owner_id, f.{face_orientation.value}_embedding <-> '[{",".join(map(str, embedding))}]' as distance
    from face f
) a
where distance < {threshold}
order by distance asc
limit 1
"""
        )
        result = session.execute(statement).first()  # type: ignore

        if result is None:
            return None

        return FaceMatch(owner_id=result[0], distance=result[1])


face = CRUDFace(Face)
