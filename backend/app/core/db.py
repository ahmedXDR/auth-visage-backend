import logging
from collections.abc import Generator
from uuid import UUID

from sqlmodel import Session, create_engine, select

from app.core.auth import get_super_client
from app.core.config import settings
from app.core.security import create_jwt_token, get_user_data, secure_token
from app.models import RefreshToken, User, new_session
from app.schemas import Token

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
        assert response.user.email == settings.FIRST_SUPERUSER
        assert response.user.id is not None
        assert response.session.access_token is not None


async def generate_user_session(user_id: UUID) -> Token:
    user_data = get_user_data(str(user_id))

    jwt_token = create_jwt_token(user_data)

    session = next(get_db())

    new_session_obj = new_session(user_id)
    session.add(new_session_obj)
    session.commit()

    refresh_token = secure_token()
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
