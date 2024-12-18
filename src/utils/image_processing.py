import base64
from io import BytesIO
from PIL import Image

def encode_image(image_file):
    """
    Encodes an image file to a base64 string.
    """
    buffered = BytesIO()
    image_file.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def encode_images(image_list):
    """
    Encodes a list of image files to a list of base64 strings.
    """
    return [encode_image(image) for image in image_list]

def add_red_border(image, border_width=10):
    """Adds a red border to the provided image."""
    width, height = image.size
    new_size = (width + 2 * border_width, height + 2 * border_width)
    bordered_image = Image.new('RGB', new_size, "red")
    bordered_image.paste(image, (border_width, border_width))
    return bordered_image

def serialize_image(image: Image.Image) -> str:
    """
    Serialize a PIL image to a base64-encoded string.
    """
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def deserialize_image(image_data: str) -> Image.Image:
    """
    Deserialize a base64-encoded string back to a PIL image.
    """
    buffer = BytesIO(base64.b64decode(image_data))
    return Image.open(buffer)
