import logging
from enum import Enum
from typing import Any

import socketio  # type: ignore
from fastapi.security import HTTPAuthorizationCredentials

from app.core.auth import get_async_super_client, get_current_user
from app.core.db import get_db
from app.core.security import get_user_data
from app.core.socket_io import sio
from app.crud import auth_code, face
from app.models.auth_code import AuthCodeCreate
from app.models.face import FaceCreate
from app.utils import generate_auth_code
from app.utils.detection import embed_largest_face, parse_frame, verify_face

logger = logging.getLogger("uvicorn")


class AuthTypes(str, Enum):
    LOGIN = "login"
    REGISTER = "register"


class AuthNamespace(socketio.AsyncNamespace):  # type: ignore
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def on_connect(
        self,
        sid: str,
        environ: dict[str, Any],
        auth: dict[str, Any],
    ) -> None:
        if auth:
            auth_header = auth.get("Authorization")

            if auth_header:
                jwt = auth_header.partition(" ")[2]
                credentials = HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=jwt,
                )
                user = await get_current_user(
                    await get_async_super_client(),
                    credentials,
                )
                await self.save_session(sid, {"user_id": user.id})

        logger.info(f"Connected: {sid}")

    async def on_start_auth(self, sid: str, data: dict[str, Any]) -> None:
        """Handles the initial authentication request"""

        code_challenge = data.get("code_challenge")
        if not code_challenge:
            await sio.emit(
                "auth_error",
                {"error": "Missing code_challenge"},
                room=sid,
            )
            return

        try:
            auth_type = AuthTypes(data.get("auth_type"))
        except ValueError as e:
            await sio.emit(
                "auth_error",
                {"error": str(e).replace("AuthTypes", "auth_type")},
                room=sid,
            )
            return

        async with sio.session(sid) as session:
            session["auth_type"] = auth_type
            session["code_challenge"] = code_challenge
            session["pending_auth"] = True

        await sio.emit("auth_started", room=sid)

    async def on_stream(self, sid: str, data: bytes) -> None:
        """Receives a video frame, processes it, and verifies authentication"""
        user_session = await self.get_session(sid)

        if not user_session.get("pending_auth", False):
            await sio.emit(
                "auth_error",
                {"error": "No auth session"},
                room=sid,
            )
            return

        try:
            frame = parse_frame(data)
        except ValueError as e:
            await sio.emit(
                "auth_error",
                {"error": str(e)},
                room=sid,
            )
            return

        largest_face_embedding = embed_largest_face(frame)

        if largest_face_embedding is None:
            await sio.emit(
                "auth_error",
                {"error": "No face detected"},
                room=sid,
            )
            return

        session = next(get_db())
        if user_session.get("auth_type") == AuthTypes.LOGIN:
            user_id = verify_face(
                session=session,
                embedding=largest_face_embedding,
            )

            if user_id is None:
                await sio.emit(
                    "auth_error",
                    {"error": "Face not recognized"},
                    room=sid,
                )
                return

            auth_obj = AuthCodeCreate(
                code=generate_auth_code(),
                code_challenge=user_session["code_challenge"],
            )

            auth_code.create(
                session=session,
                owner_id=user_id,
                obj_in=auth_obj,
            )

            await sio.emit(
                "auth_success",
                {
                    "auth_code": auth_obj.code,
                },
                room=sid,
            )
        elif user_session.get("auth_type") == AuthTypes.REGISTER:
            user_id = user_session.get("user_id", None)
            if user_id is None:
                await sio.emit(
                    "auth_error",
                    {"error": "Not authenticated"},
                    room=sid,
                )
                await sio.disconnect(sid)
                return

            user_data = get_user_data(str(user_id))
            if not user_data:
                await sio.emit(
                    "auth_error",
                    {"error": "User not found"},
                    room=sid,
                )
                await sio.disconnect(sid)

            # save face embedding
            face.create(
                session=session,
                owner_id=user_id,
                obj_in=FaceCreate(
                    embedding=largest_face_embedding,
                ),
            )

            await sio.emit(
                "auth_success",
                {"user_id": user_id},
                room=sid,
            )
            await sio.disconnect(sid)

    async def on_disconnect(self, sid: str) -> None:
        """Handles disconnection events"""
        logger.info(f"Disconnected: {sid}")
