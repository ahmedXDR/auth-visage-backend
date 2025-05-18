import logging
from enum import Enum
from typing import Any
from uuid import UUID

import socketio  # type: ignore
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlmodel import Session

from app.core.auth import get_async_super_client, get_current_user
from app.core.config import settings
from app.core.db import generate_supabase_session, get_db
from app.core.socket_io import sio
from app.crud import auth_code, face, oauth_session, user_project_link
from app.models.auth_code import AuthCodeCreate
from app.models.face import FaceCreate
from app.utils import generate_auth_code
from app.utils.detection import extract_largest_face, parse_frame
from app.utils.errors import FaceSpoofingDetected

logger = logging.getLogger("uvicorn")


class AuthTypes(str, Enum):
    """Authentication types supported by the WebSocket interface."""

    OAUTH = "oauth"
    LOGIN = "login"
    REGISTER = "register"


class SioUserSession(BaseModel):
    user_id: str | None = None
    origin: str | None = None
    pending_oauth: bool = False
    auth_type: AuthTypes | None = None
    code_challenge: str | None = None
    oauth_session_uuid: UUID | None = None


class AuthNamespace(socketio.AsyncNamespace):  # type: ignore
    """WebSocket namespace for handling authentication flows.

    This namespace manages real-time authentication processes including:
    - OAuth authentication
    - Face-based login
    - Face registration
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the authentication namespace."""
        super().__init__(*args, **kwargs)

    async def emit_error(
        self, sid: str, error: str, disconnect: bool = False
    ) -> None:
        """Emit an error message to the client and optionally disconnect them.

        Args:
            sid: The session ID of the client
            error: The error message to send
            disconnect: Whether to disconnect the client after sending the error
        """
        await sio.emit(
            "auth_error",
            {"error": error},
            room=sid,
        )
        if disconnect:
            await sio.disconnect(sid)

    async def on_connect(
        self,
        sid: str,
        environ: dict[str, Any],
        auth: dict[str, Any] | None = None,
    ) -> None:
        """Handle new WebSocket connections.

        Args:
            sid: Session ID of the connecting client
            environ: Connection environment information
            auth: Optional authentication data
        """
        user_id = None
        user_id = "635a382d-1ccf-497d-b98e-fa958cfc316e"
        if auth and (auth_header := auth.get("authorization")):
            jwt = auth_header.partition(" ")[2]
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=jwt,
            )
            user_id = (
                await get_current_user(
                    await get_async_super_client(),
                    credentials,
                )
            ).id

        await self.save_session(
            sid,
            SioUserSession(
                user_id=user_id,
                origin=environ.get("HTTP_ORIGIN"),
            ),
        )

        logger.info(f"Connected: {sid}")

    async def on_start_auth(
        self,
        sid: str,
        data: dict[str, Any],
    ) -> None:
        """Handle the initial authentication request.

        Args:
            sid: Session ID of the client
            data: Authentication request data containing auth_type and optional parameters
        """
        try:
            auth_type = AuthTypes(data.get("auth_type"))
        except ValueError as e:
            await self.emit_error(
                sid, str(e).replace("AuthTypes", "auth_type")
            )
            return

        oauth_session_uuid = None
        if oauth_session_id := data.get("oauth_session_id"):
            try:
                oauth_session_uuid = UUID(oauth_session_id)
            except ValueError:
                await self.emit_error(sid, "Invalid oauth_session_id")
                return

        async with sio.session(sid) as session:
            session.oauth_session_uuid = oauth_session_uuid
            session.auth_type = auth_type
            session.code_challenge = data.get("code_challenge")
            session.pending_oauth = True

        await sio.emit("auth_started", room=sid)

    async def _handle_register(
        self,
        sid: str,
        db_session: Session,
        user_session: SioUserSession,
        face_embedding: list[float],
    ) -> None:
        """Handle face registration process.

        Args:
            sid: Session ID of the client
            db_session: Database session
            user_session: User session data
            face_embedding: Face embedding vector
        """
        if not (session_user_id := user_session.user_id):
            await self.emit_error(sid, "Not authenticated", disconnect=True)
            return

        face.create(
            session=db_session,
            owner_id=UUID(session_user_id),
            obj_in=FaceCreate(embedding=face_embedding),
        )

        await sio.emit(
            "auth_success",
            {"user_id": session_user_id},
            room=sid,
        )
        await sio.disconnect(sid)

    async def _handle_login(
        self,
        sid: str,
        db_session: Session,
        user_session: SioUserSession,
        face_embedding: list[float],
    ) -> None:
        """Handle face-based login process.

        Args:
            sid: Session ID of the client
            db_session: Database session
            user_session: User session data
            face_embedding: Face embedding vector
        """
        if not (origin := user_session.origin):
            await self.emit_error(sid, "Missing origin", disconnect=True)
            return

        if origin.rstrip("/") not in settings.all_trusted_login_origins:
            await self.emit_error(sid, "Invalid origin", disconnect=True)
            return

        match = face.face_match(
            session=db_session,
            embedding=face_embedding,
            threshold=settings.FACE_MATCH_THRESHOLD,
        )
        if not match:
            await self.emit_error(sid, "Face not recognized")
            return

        session_data = generate_supabase_session(match.owner_id)
        await sio.emit(
            "auth_success",
            session_data.model_dump(),
            room=sid,
        )
        await sio.disconnect(sid)

    async def _handle_oauth(
        self,
        sid: str,
        db_session: Session,
        user_session: SioUserSession,
        face_embedding: list[float],
    ) -> None:
        """Handle OAuth authentication process.

        Args:
            sid: Session ID of the client
            db_session: Database session
            user_session: User session data
            face_embedding: Face embedding vector
        """

        if not (code_challenge := user_session.code_challenge):
            await self.emit_error(sid, "Missing code_challenge")
            return

        if not (oauth_session_id := user_session.oauth_session_uuid):
            await self.emit_error(sid, "Missing oauth_session_id")
            return

        if not (
            oauth_session_obj := oauth_session.get(
                session=db_session,
                id=oauth_session_id,
            )
        ):
            await self.emit_error(sid, "Invalid oauth_session_id")
            return

        if not (
            match := face.face_match(
                session=db_session,
                embedding=face_embedding,
                threshold=settings.FACE_MATCH_THRESHOLD,
            )
        ):
            await self.emit_error(sid, "Face not recognized")
            return

        if not (
            user_project_link.get(
                session=db_session,
                owner_id=match.owner_id,
                project_id=oauth_session_obj.project_id,
            )
        ):
            await self.emit_error(sid, "User not linked to project")
            return

        auth_obj = AuthCodeCreate(
            code=generate_auth_code(),
            code_challenge=code_challenge,
            project_id=oauth_session_obj.project_id,
        )

        auth_code.create(
            session=db_session,
            owner_id=match.owner_id,
            obj_in=auth_obj,
        )

        await sio.emit(
            "auth_success",
            {"auth_code": auth_obj.code},
            room=sid,
        )

    async def on_stream(self, sid: str, data: bytes) -> None:
        """Process video stream frames for authentication.

        Args:
            sid: Session ID of the client
            data: Raw video frame data
        """
        user_session = SioUserSession(
            **(await self.get_session(sid)).model_dump()
        )

        if not user_session.pending_oauth:
            await self.emit_error(
                sid,
                "Start auth first by calling event 'start_auth'",
            )
            return

        try:
            frame = parse_frame(data)
        except ValueError as e:
            await self.emit_error(sid, str(e))
            return

        try:
            largest_face = extract_largest_face(
                frame,
                anti_spoofing=True,
                embed=True,
            )
        except FaceSpoofingDetected:
            await self.emit_error(sid, "No valid face detected")
            return

        if largest_face is None:
            await self.emit_error(sid, "No valid face detected")
            return

        db_session = next(get_db())
        match user_session.auth_type:
            case AuthTypes.REGISTER:
                await self._handle_register(
                    sid,
                    db_session,
                    user_session,
                    largest_face["embedding"],
                )
            case AuthTypes.LOGIN:
                await self._handle_login(
                    sid,
                    db_session,
                    user_session,
                    largest_face["embedding"],
                )
            case AuthTypes.OAUTH:
                await self._handle_oauth(
                    sid,
                    db_session,
                    user_session,
                    largest_face["embedding"],
                )

    async def on_disconnect(self, sid: str) -> None:
        """Handle client disconnection events.

        Args:
            sid: Session ID of the disconnecting client
        """
        logger.info(f"Disconnected: {sid}")
