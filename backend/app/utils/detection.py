import io
import logging
from enum import Enum
from typing import Any
from uuid import UUID

from deepface import DeepFace  # type: ignore
from numpy import array
from PIL import Image
from sqlmodel import Session, text

from app.core.config import settings
from app.crud import face


class Models(str, Enum):
    VGG_FACE = "VGG-Face"
    FACENET = "Facenet"
    FACENET512 = "Facenet512"
    OPENFACE = "OpenFace"
    DEEPFACE = "DeepFace"
    DEEPID = "DeepID"
    ARCFACE = "ArcFace"
    DLIB = "Dlib"
    SFACE = "SFace"
    GHOSTFACENET = "GhostFaceNet"


class Backends(str, Enum):
    OPENCV = "opencv"
    SSD = "ssd"
    DLIB = "dlib"
    MTCNN = "mtcnn"
    RETINA_FACE = "retinaface"
    MEDIAPIPE = "mediapipe"
    YOLOV8 = "yolov8"
    YUNET = "yunet"
    FASTMTCNN = "fastmtcnn"


logger = logging.getLogger("uvicorn")


MODEL_NAME = Models.FACENET
DETECTOR_BACKEND = Backends.OPENCV


def parse_frame(data: bytes) -> Image.Image:
    try:
        image_stream = io.BytesIO(data)
        image_stream.seek(0)
        return Image.open(image_stream)
    except Exception:
        raise ValueError("Invalid image data")


def get_largest_face_location(image: Image.Image) -> dict[str, Any]:
    """
    Load an image file and return the location of the largest face in the
    image.

    Args:
        image: image file name or file object to load.

    Returns:
        result (Dict[str, Any]): The detected face's regions as a dictionary
        containing:
        - keys 'x', 'y', 'w', 'h' with int values
        - keys 'left_eye', 'right_eye' with a tuple of 2 ints as values.
        left and right eyes
            are eyes on the left and right respectively with respect to
            the person itself
            instead of observer.
    """

    face_objs = DeepFace.extract_faces(
        array(image),
        # anti_spoofing=True,
    )

    largest_face = max(
        face_objs,
        key=lambda face: face["facial_area"]["w"] * face["facial_area"]["h"],
    )
    largest_facial_area: dict[str, Any] = largest_face["facial_area"]

    return largest_facial_area


def embed_largest_face(
    image: Image.Image,
) -> list[float] | None:
    """
    Load an image file and return the embedding of the largest face in the
    image.

    Args:
        image: image file name or file object to load.

    Returns:
        result (list[float]): The detected face's embedding.
    """
    try:
        embedding_objs = DeepFace.represent(
            array(image),
            model_name=MODEL_NAME,
        )

        largest_face = max(
            embedding_objs,
            key=lambda face: (
                face["facial_area"]["w"] * face["facial_area"]["h"]
            ),
        )

        largest_face_embedding = largest_face["embedding"]

        return largest_face_embedding
    except ValueError as e:
        logger.error(f"Error embedding largest face: {e}")
        return None


def verify_face(
    session: Session,
    embedding: list[float],
) -> UUID | None:
    """Verify the face embedding against the database

    Args:
        session: The database session
        embedding: The face embedding

    Returns:
        UUID | None: The user id
    """

    statement = text(f"""
select *
from (
    select f.id, f.embedding <-> '{str(embedding)}' as distance
    from face f
) a
where distance < {settings.FACE_MATCH_THRESHOLD}
order by distance asc
limit 1
""")

    result = session.exec(statement).all()

    if not result:
        return None

    face_match_result = result[0]
    if not face_match_result:
        return None

    face_obj = face.get(session=session, id=face_match_result[0])

    if face_obj is None:
        return None

    return face_obj.owner_id
