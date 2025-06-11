import logging
from collections.abc import Generator
from secrets import token_urlsafe
from uuid import UUID

from sqlmodel import Session, create_engine, select

from app.core.auth import get_super_client
from app.core.config import settings
from app.core.security import (
    create_jwt_token,
    create_supabase_jwt_token,
    get_user_data,
)
from app.crud import oauth_refresh_token, oauth_session
from app.models import RefreshToken, User
from app.models.oauth_refresh_token import (
    OAuthRefreshToken,
    OAuthRefreshTokenCreate,
)
from app.models.oauth_session import (
    OAuthSession,
    OAuthSessionCreate,
    OAuthSessionUpdate,
)
from app.models.session import new_session
from app.schemas import OAuthToken, Token

# make sure all SQLModel models are imported (app.models) before initializing
# DB otherwise, SQLModel might fail to initialize relationships properly.
# for more details:
# https://github.com/fastapi/full-stack-fastapi-template/issues/28
logger = logging.getLogger("uvicorn")
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def get_db() -> Generator[Session, None]:
    with Session(engine) as session:
        yield session


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel
    # # This works because the models are already imported and registered
    # # from app.models
    # SQLModel.metadata.create_all(engine)

    result = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER),
    )
    user = result.first()
    if not user:
        super_client = get_super_client()
        response = super_client.auth.sign_up(
            {
                "email": settings.FIRST_SUPERUSER,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
            }
        )
        assert response.user is not None
        assert response.user.email == settings.FIRST_SUPERUSER
        assert response.user.id is not None
        assert response.session is not None
        assert response.session.access_token is not None


def generate_oauth_token(
    session: Session,
    user_id: UUID,
    project_id: UUID,
) -> OAuthToken:
    if not (user_data := get_user_data(user_id)):
        raise ValueError("User not found")

    oauth_session_obj = oauth_session.create(
        session,
        obj_in=OAuthSessionCreate(
            project_id=project_id,
        ),
        owner_id=user_id,
    )

    oauth_refresh_token_obj = oauth_refresh_token.create(
        session,
        obj_in=OAuthRefreshTokenCreate(
            oauth_session_id=oauth_session_obj.id,
        ),
        owner_id=user_id,
    )

    oauth_token = OAuthToken(
        oauth_session_id=oauth_session_obj.id,
        access_token=create_jwt_token(user_data),
        refresh_token=oauth_refresh_token_obj.token,
        expires_in=settings.JWT_lifespan,
    )

    return oauth_token


def refresh_oauth_token(
    session: Session,
    refresh_token: OAuthRefreshToken,
    oauth_session_obj: OAuthSession,
) -> OAuthToken:
    if not (user_data := get_user_data(refresh_token.owner_id)):
        raise ValueError("User not found")

    # create a new refresh token
    new_oauth_refresh_token_obj = oauth_refresh_token.create(
        session,
        obj_in=OAuthRefreshTokenCreate(
            oauth_session_id=oauth_session_obj.id,
        ),
        owner_id=refresh_token.owner_id,
    )
    oauth_session.update(
        session,
        id=oauth_session_obj.id,
        obj_in=OAuthSessionUpdate(
            project_id=oauth_session_obj.project_id,
            refreshed_at=new_oauth_refresh_token_obj.created_at,
        ),
    )

    # delete the old refresh token
    oauth_refresh_token.remove(session, id=refresh_token.id)

    oauth_token = OAuthToken(
        oauth_session_id=oauth_session_obj.id,
        access_token=create_jwt_token(user_data),
        refresh_token=new_oauth_refresh_token_obj.token,
        expires_in=settings.JWT_lifespan,
    )

    return oauth_token


def generate_supabase_session(user_id: UUID) -> Token:
    if not (user_data := get_user_data(user_id)):
        raise ValueError("User not found")

    jwt_token = create_supabase_jwt_token(user_data)

    session = next(get_db())

    new_session_obj = new_session(user_id)
    session.add(new_session_obj)
    session.commit()

    refresh_token = token_urlsafe(16)
    refresh_token_obj = RefreshToken(
        token=refresh_token,
        user_id=user_id,
        session_id=new_session_obj.id,
    )
    session.add(refresh_token_obj)
    session.commit()

    token = Token(
        access_token=jwt_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_lifespan,
    )

    return token
