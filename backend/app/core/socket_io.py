import socketio  # type: ignore

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
)
