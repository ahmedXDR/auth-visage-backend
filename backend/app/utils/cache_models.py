from PIL import Image

from app.utils.detection import extract_largest_face


def cache_models() -> None:
    fake_image = Image.new(
        "RGB",
        (100, 100),
        color="red",
    )
    extract_largest_face(
        fake_image,
        embed=True,
    )


if __name__ == "__main__":
    cache_models()
