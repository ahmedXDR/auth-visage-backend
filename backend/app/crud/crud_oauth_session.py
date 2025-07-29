from app.crud.base import CRUDBase
from app.models.oauth_session import (
    OAuthSession,
    OAuthSessionCreate,
    OAuthSessionUpdate,
)


class CRUDOAuthSession(
    CRUDBase[
        OAuthSession,
        OAuthSessionCreate,
        OAuthSessionUpdate,
    ],
):
    pass


oauth_session = CRUDOAuthSession(OAuthSession)
