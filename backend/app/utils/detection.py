import io
import logging
from enum import Enum
from typing import Any

from deepface import DeepFace  # type: ignore
from numpy import array
from PIL import Image


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


def get_largest_face_location(image: Image.Image) -> dict[str, Any] | None:
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
    try:
        face_objs = DeepFace.extract_faces(
            array(image),
            detector_backend=DETECTOR_BACKEND,
        )
    except ValueError as e:
        logger.error(f"Error extracting faces: {e}")
        return None

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
            detector_backend=DETECTOR_BACKEND,
            max_faces=1,
        )
    except ValueError as e:
        logger.error(f"Error embedding largest face: {e}")
        return None

    largest_face = embedding_objs[0]

    largest_face_embedding: list[float] = largest_face["embedding"]

    return largest_face_embedding
