import uuid

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.auth_code import AuthCode, AuthCodeCreate


class CRUDAuthCode(CRUDBase[AuthCode, AuthCodeCreate, AuthCodeCreate]):
    def get_by_code(self, session: Session, *, code: str) -> AuthCode | None:
        """Get a single record by code"""
        statement = select(self.model).where(self.model.code == code)
        result = session.exec(statement)
        return result.one_or_none()

    def create(
        self, session: Session, *, owner_id: uuid.UUID, obj_in: AuthCodeCreate
    ) -> AuthCode:
        return super().create(session, owner_id=owner_id, obj_in=obj_in)


auth_code = CRUDAuthCode(AuthCode)
