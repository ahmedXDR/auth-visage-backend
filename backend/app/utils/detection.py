import io
import logging
from enum import Enum
from typing import Any

from deepface import DeepFace  # type: ignore
from numpy import array
from PIL import Image

from app.core.config import settings
from app.utils.errors import FaceSpoofingDetected


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
DETECTOR_BACKEND = Backends.RETINA_FACE


def parse_frame(data: bytes) -> Image.Image:
    try:
        image_stream = io.BytesIO(data)
        image_stream.seek(0)
        return Image.open(image_stream)
    except Exception:
        raise ValueError("Invalid image data")


def extract_largest_face(
    image: Image.Image,
    anti_spoofing=False,
    embed=False,
) -> dict[str, Any] | None:
    """
    Extract the largest face from a given image

    Args:
        image (Image.Image): Image object.
        anti_spoofing (boolean): Flag to enable anti spoofing (default is False).
        embed (boolean): Flag to embed the extracted face (default is False).

    Returns:
        results (Dict[str, Any]): A dictionary which contains:

        - "face" (np.ndarray): The detected face as a NumPy array.

        - "facial_area" (Dict[str, Any]): The detected face's regions as a dictionary containing:
            - keys 'x', 'y', 'w', 'h' with int values
            - keys 'left_eye', 'right_eye' with a tuple of 2 ints as values. left and right eyes
                are eyes on the left and right respectively with respect to the person itself
                instead of observer.

        - "confidence" (float): The confidence score associated with the detected face.

        - "is_real" (boolean): antispoofing analyze result. this key is just available in the
            result only if anti_spoofing is set to True in input arguments.

        - "antispoof_score" (float): score of antispoofing analyze result. this key is
            just available in the result only if anti_spoofing is set to True in input arguments.

        - "embedding" (List[float]): Multidimensional vector representing facial features.
            The number of dimensions varies based on the reference model (e.g., FaceNet
            returns 128 dimensions, VGG-Face returns 4096 dimensions).
    """
    try:
        face_objs = DeepFace.extract_faces(
            array(image),
            detector_backend=DETECTOR_BACKEND,
            align=True,
            anti_spoofing=anti_spoofing,
        )
    except ValueError as e:
        if "face could not be detected" not in str(e).lower():
            logger.error(f"Error extracting face: {e}")
        return None

    largest_face_obj = max(
        face_objs,
        key=lambda face_obj: face_obj["facial_area"]["w"]
        * face_obj["facial_area"]["h"],
    )

    if (
        anti_spoofing
        and not largest_face_obj["is_real"]
        and largest_face_obj["antispoof_score"] > settings.ANTI_SPOOF_THRESHOLD
    ):
        raise FaceSpoofingDetected("Face spoofing detected")

    if embed:
        try:
            embedding = DeepFace.represent(
                largest_face_obj["face"],
                model_name=MODEL_NAME,
                detector_backend="skip",
                max_faces=1,
            )[0]["embedding"]

            largest_face_obj["embedding"] = embedding
        except ValueError as e:
            logger.error(f"Error embedding face: {e}")
            return None

    return largest_face_obj
