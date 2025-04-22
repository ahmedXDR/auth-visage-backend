from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.auth_code import AuthCode, AuthCodeCreate, AuthCodeUpdate


class CRUDAuthCode(
    CRUDBase[
        AuthCode,
        AuthCodeCreate,
        AuthCodeUpdate,
    ],
):
    def create(
        self,
        session: Session,
        *,
        obj_in: AuthCodeCreate,
        owner_id: UUID | None = None,
    ) -> AuthCode:
        if owner_id is None:
            raise ValueError("owner_id is required")

        return super().create(session, obj_in=obj_in, owner_id=owner_id)

    def get_by_code(self, session: Session, *, code: str) -> AuthCode | None:
        """Get a single record by code"""
        statement = select(self.model).where(self.model.code == code)
        result = session.exec(statement)
        return result.one_or_none()


auth_code = CRUDAuthCode(AuthCode)
