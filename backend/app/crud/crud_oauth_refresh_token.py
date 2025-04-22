from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.oauth_refresh_token import (
    OAuthRefreshToken,
    OAuthRefreshTokenCreate,
    OAuthRefreshTokenUpdate,
)


class CRUDOAuthRefreshToken(
    CRUDBase[
        OAuthRefreshToken,
        OAuthRefreshTokenCreate,
        OAuthRefreshTokenUpdate,
    ],
):
    def get_by_token(
        self,
        session: Session,
        *,
        token: str,
    ) -> OAuthRefreshToken | None:
        """Get a single record by token"""
        statement = select(self.model).where(self.model.token == token)
        result = session.exec(statement)
        return result.one_or_none()


oauth_refresh_token = CRUDOAuthRefreshToken(OAuthRefreshToken)
