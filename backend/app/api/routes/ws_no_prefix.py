import base64
import logging
from typing import Any
from uuid import UUID

import socketio  # type: ignore
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from app.core.auth import get_async_super_client, get_current_user
from app.core.config import settings
from app.core.db import generate_supabase_session, get_db
from app.crud import (
    auth_code,
    face,
    oauth_session,
    project,
    user_project_link,
)
from app.models.auth_code import AuthCodeCreate
from app.models.face import FaceCreate, FaceOrientation
from app.models.user_project_link import UserProjectLinkCreate
from app.schemas.auth import AuthTypes, SioUserSession
from app.utils import generate_auth_code
from app.utils.detection import extract_largest_face, parse_frame
from app.utils.errors import FaceSpoofingDetected

logger = logging.getLogger("uvicorn")


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
        await self.emit(
            "auth_error",
            {"error": error},
            room=sid,
        )
        if disconnect:
            await self.disconnect(sid)

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

        async with self.session(sid) as session:
            session.oauth_session_uuid = oauth_session_uuid
            session.auth_type = auth_type
            session.code_challenge = data.get("code_challenge")
            session.pending_oauth = True

        await self.emit("auth_started", room=sid)

    async def _handle_register(
        self,
        sid: str,
        db_session: Session,
        face_embedding: list[float],
        face_orientation: FaceOrientation,
    ) -> None:
        """Handle face registration process.

        Args:
            sid: Session ID of the client
            db_session: Database session
            face_embedding: Face embedding vector
        """
        try:
            async with self.session(sid) as session:
                if not (session_user_id := session.user_id):
                    await self.emit_error(
                        sid, "Not authenticated", disconnect=True
                    )
                    return

                if session.face_data is None:
                    if face_orientation != FaceOrientation.CENTER:
                        await self.emit(
                            "set_orientation",
                            FaceOrientation.CENTER.value,
                            room=sid,
                        )
                        return

                    session.face_data = FaceCreate(
                        center_embedding=face_embedding,
                        left_embedding=None,
                        right_embedding=None,
                    )
                    await self.emit(
                        "set_orientation",
                        FaceOrientation.RIGHT.value,
                        room=sid,
                    )
                    return

                if session.face_data.right_embedding is None:
                    if face_orientation != FaceOrientation.RIGHT:
                        await self.emit(
                            "set_orientation",
                            FaceOrientation.RIGHT.value,
                            room=sid,
                        )
                        return

                    session.face_data.right_embedding = face_embedding
                    await self.emit(
                        "set_orientation",
                        FaceOrientation.LEFT.value,
                        room=sid,
                    )
                    return

                if session.face_data.left_embedding is None:
                    if face_orientation != FaceOrientation.LEFT:
                        await self.emit(
                            "set_orientation",
                            FaceOrientation.LEFT.value,
                            room=sid,
                        )
                        return

                    session.face_data.left_embedding = face_embedding

                face.create(
                    session=db_session,
                    owner_id=UUID(session_user_id),
                    obj_in=session.face_data,
                )

                await self.emit(
                    "auth_success",
                    {"user_id": session_user_id},
                    room=sid,
                )
                await self.disconnect(sid)
        except KeyError:
            return

    async def _handle_login(
        self,
        sid: str,
        db_session: Session,
        user_session: SioUserSession,
        face_embedding: list[float],
        face_orientation: FaceOrientation,
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

        if face_orientation != user_session.random_orientation:
            await self.emit(
                "set_orientation",
                user_session.random_orientation.value,
                room=sid,
            )
            return

        if not (
            match := face.face_match(
                session=db_session,
                embedding=face_embedding,
                face_orientation=face_orientation,
                threshold=settings.FACE_MATCH_THRESHOLD,
            )
        ):
            await self.emit_error(sid, "Face not recognized")
            return

        session_data = generate_supabase_session(match.owner_id)
        await self.emit(
            "auth_success",
            session_data.model_dump(),
            room=sid,
        )
        await self.disconnect(sid)

    async def _handle_oauth(
        self,
        sid: str,
        db_session: Session,
        user_session: SioUserSession,
        face_embedding: list[float],
        face_orientation: FaceOrientation,
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

        if face_orientation != user_session.random_orientation:
            await self.emit(
                "set_orientation",
                user_session.random_orientation.value,
                room=sid,
            )
            return

        if not (
            match := face.face_match(
                session=db_session,
                embedding=face_embedding,
                face_orientation=face_orientation,
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
            async with self.session(sid) as session:
                session.user_id = str(match.owner_id)

            await self.emit(
                "capture_consent",
                {
                    "project": project.get(
                        db_session,
                        id=oauth_session_obj.project_id,
                    ).model_dump_json(),
                },
            )
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

        await self.emit(
            "auth_success",
            {"auth_code": auth_obj.code},
            room=sid,
        )

    async def on_stream(self, sid: str, data: dict) -> None:
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

        if type(data) is not dict:
            await self.emit_error(sid, "Invalid data type, must be dict")
            return

        if not (raw_frame := data.get("frame")):
            await self.emit_error(sid, "Missing frame data")
            return

        if type(raw_frame) is str:
            try:
                raw_frame = base64.b64decode(raw_frame)
            except ValueError:
                await self.emit_error(sid, "Invalid frame data format")
                return

        if type(raw_frame) is not bytes:
            await self.emit_error(sid, "Invalid frame data type")
            return

        if not (frame_orientation := data.get("orientation")):
            await self.emit_error(sid, "Missing frame orientation")
            return

        try:
            frame_orientation = FaceOrientation(frame_orientation)
        except ValueError:
            await self.emit_error(sid, "Invalid frame orientation value")
            return

        try:
            frame = parse_frame(raw_frame)
        except ValueError as e:
            await self.emit_error(sid, str(e))
            return

        # async with self.session(sid) as session:
        #     if len(session.liveness_frames) < 4:
        #         session.liveness_frames.append(frame)
        #         return
        #     elif len(session.liveness_frames) == 4:
        #         session.liveness_frames.append(frame)
        #     else:
        #         session.liveness_frames = [frame]
        #         return

        # liveness_score = infer_liveness_from_frames(
        #     [user_session.liveness_frames]
        # )[0]
        # if liveness_score < settings.LIVENESS_THRESHOLD:
        #     await self.emit_error(sid, "Liveness check failed")
        #     return

        try:
            largest_face = extract_largest_face(
                frame,
                anti_spoofing=True,
                embed=True,
            )
        except FaceSpoofingDetected:
            await self.emit_error(sid, "Spoofing detected")
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
                    largest_face["embedding"],
                    frame_orientation,
                )
            case AuthTypes.LOGIN:
                await self._handle_login(
                    sid,
                    db_session,
                    user_session,
                    largest_face["embedding"],
                    frame_orientation,
                )
            case AuthTypes.OAUTH:
                await self._handle_oauth(
                    sid,
                    db_session,
                    user_session,
                    largest_face["embedding"],
                    frame_orientation,
                )

    async def on_consent_captured(self, sid: str) -> None:
        """Handle user consent for OAuth project capture.

        Args:
            sid: Session ID of the client
            data: Consent data containing project ID and consent status
        """
        db_session = next(get_db())
        user_session = SioUserSession(
            **(await self.get_session(sid)).model_dump()
        )

        if not (user_id := user_session.user_id):
            await self.emit_error(sid, "Unknown user")
            return

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

        project_id = oauth_session_obj.project_id

        user_project_link.create(
            session=db_session,
            owner_id=UUID(user_id),
            obj_in=UserProjectLinkCreate(
                project_id=project_id,
            ),
        )

        auth_obj = AuthCodeCreate(
            code=generate_auth_code(),
            code_challenge=code_challenge,
            project_id=oauth_session_obj.project_id,
        )

        auth_code.create(
            session=db_session,
            obj_in=auth_obj,
            owner_id=UUID(user_id),
        )

        await self.emit(
            "auth_success",
            {"auth_code": auth_obj.code},
            room=sid,
        )

    async def on_disconnect(self, sid: str) -> None:
        """Handle client disconnection events.

        Args:
            sid: Session ID of the disconnecting client
        """
        logger.info(f"Disconnected: {sid}")
