from PIL import Image

from app.utils.detection import embed_largest_face, get_largest_face_location


def cache_models():
    fake_image = Image.new("RGB", (100, 100), color="red")
    get_largest_face_location(fake_image)
    embed_largest_face(fake_image)


if __name__ == "__main__":
    cache_models()
