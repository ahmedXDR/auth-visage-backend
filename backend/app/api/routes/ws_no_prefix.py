import socketio

from app.core.socket_io import sio
from app.utils.detection import get_largest_face_location, parse_frame


class NoPrefixNamespace(socketio.AsyncNamespace):
    def on_connect(self, sid, environ):
        print("connect ", sid)

    async def on_message(self, sid, data):
        print("message ", data)
        await sio.emit("response", "hi " + data)

    def on_disconnect(self, sid):
        print("disconnect ", sid)

    async def on_stream(self, sid, data):
        frame = parse_frame(data)
        largest_face_location = get_largest_face_location(frame)
        if largest_face_location is None:
            await sio.emit("response", "No face detected")
        else:
            await sio.emit("response", largest_face_location)
