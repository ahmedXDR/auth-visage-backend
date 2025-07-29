from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.trusted_origin import (
    TrustedOrigin,
    TrustedOriginCreate,
    TrustedOriginUpdate,
)


class CRUDTrustedOrigin(
    CRUDBase[
        TrustedOrigin,
        TrustedOriginCreate,
        TrustedOriginUpdate,
    ],
):
    def create(
        self,
        session: Session,
        *,
        obj_in: TrustedOriginCreate,
        owner_id: UUID | None = None,
    ) -> TrustedOrigin:
        if owner_id is None:
            raise ValueError("owner_id is required")

        return super().create(session, obj_in=obj_in, owner_id=owner_id)

    def get_by_name_and_project(
        self,
        session: Session,
        *,
        name: str,
        project_id: UUID,
    ) -> TrustedOrigin | None:
        """Get a single record by name"""
        statement = select(self.model).where(
            self.model.name == name,
            self.model.project_id == project_id,
        )
        result = session.exec(statement)
        return result.one_or_none()

    def get_multi_by_owner_and_project(
        self,
        session: Session,
        *,
        owner_id: UUID,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[TrustedOrigin]:
        statement = (
            select(self.model)
            .where(
                self.model.owner_id == owner_id,
                self.model.project_id == project_id,
            )
            .offset(skip)
            .limit(limit)
        )
        result = session.exec(statement)
        return result.all()


trusted_origin = CRUDTrustedOrigin(TrustedOrigin)
