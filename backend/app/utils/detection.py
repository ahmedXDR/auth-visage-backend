import io
from typing import Any, List, Union

import numpy as np
from PIL import Image, ImageDraw
from deepface import DeepFace

models = [
    "VGG-Face",
    "Facenet",
    "Facenet512",
    "OpenFace",
    "DeepFace",
    "DeepID",
    "ArcFace",
    "Dlib",
    "SFace",
    "GhostFaceNet",
]

backends = [
    "opencv",
    "ssd",
    "dlib",
    "mtcnn",
    "retinaface",
    "mediapipe",
    "yolov8",
    "yunet",
    "fastmtcnn",
]

metrics = ["cosine", "euclidean", "euclidean_l2"]

MODEL_NAME = models[9]
DETECTOR_BACKEND = backends[0]
DISTANCE_METRIC = metrics[2]


def parse_frame(data) -> Image.Image:

    try:
        image_stream = io.BytesIO(data)
        image_stream.seek(0)
        return Image.open(image_stream)
    except Exception:
        raise ValueError("Invalid image data")


def get_largest_face_location(image: Image.Image):
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
        np.array(image),
        anti_spoofing=True,
    )

    largest_face = max(
        face_objs,
        key=lambda face: face["facial_area"]["w"] * face["facial_area"]["h"],
    )
    largest_facial_area: dict[str, Any] = largest_face["facial_area"]

    draw = ImageDraw.Draw(image)
    draw.rectangle(
        [
            largest_facial_area["x"],
            largest_facial_area["y"],
            largest_facial_area["x"] + largest_facial_area["w"],
            largest_facial_area["y"] + largest_facial_area["h"],
        ],
        outline="red",
    )

    return largest_facial_area


def embed_largest_face(
    image: Image.Image,
) -> Union[np.ndarray, None]:
    """
    Load an image file and return the facial embedding for the largest face in
    the image using DeepFace.

    Args:
        image_file: image file name or file object to load.
    Returns:
        The facial embedding for the largest face in the image or None.
    """

    try:
        embedding_objs = DeepFace.represent(
            np.array(image),
            detector_backend=DETECTOR_BACKEND,
            model_name=MODEL_NAME,
        )

        largest_face = max(
            embedding_objs,
            key=lambda face: (
                face["facial_area"]["w"] * face["facial_area"]["h"]
            ),
        )
        largest_face_embedding = np.array(largest_face["embedding"])

        return largest_face_embedding
    except ValueError:
        return None


def find_best_match(
    image: Image.Image,
    embeddings: List[np.ndarray],
    similarity_threshold=None,
):
    """
    Find the best match for the largest face in an image using DeepFace.

    :param image_file: image file name or file object to load.
    :param embeddings: List of embeddings to compare against.
    :param similarity_threshold: The minimum similarity threshold to consider
    a match.
    :return: The index of the best match in the embeddings list or None if no
    match.
    """
    if not embeddings:
        return None

    if similarity_threshold is None:
        similarity_threshold = DeepFace.verification.find_threshold(
            MODEL_NAME,
            DISTANCE_METRIC,
        )

    largest_face_embedding = embed_largest_face(image)

    if largest_face_embedding is None:
        return None

    # Initialize variables to store the best match information
    best_match_index = None
    best_match_distance = float("inf")

    # Iterate over all embeddings to find the best match
    for i, candidate_embedding in enumerate(embeddings):
        # Calculate the Euclidean L2 distance
        distance = DeepFace.verification.find_distance(
            largest_face_embedding,
            candidate_embedding,
            DISTANCE_METRIC,
        )

        # Update the best match if this distance is smaller than the current
        # best and less than the threshold.
        if distance < best_match_distance and distance < similarity_threshold:
            best_match_distance = distance
            best_match_index = i

    return best_match_index
