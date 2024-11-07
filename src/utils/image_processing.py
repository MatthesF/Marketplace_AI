import base64
from io import BytesIO
from PIL import Image


def encode_image(image_file):
    """
    Encodes an image file to a base64 string.
    """
    buffered = BytesIO()
    image_file.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def encode_images(image_list):
    """
    Encodes a list of image files to a list of base64 strings.
    """
    return [encode_image(image) for image in image_list]


def add_colored_border(im, border_width=20, color=(0.99, 0.0, 0.0, 0.95)):
    """
    Adds a colored border to the image.

    Parameters:
    - im: The input image.
    - border_width: The width of the border.
    - color: A tuple representing the RGBA color of the border.
    """
    im[:, :border_width, :] = color  # left side
    im[:, -border_width:, :] = color  # right side
    im[:border_width, :, :] = color  # top side
    im[-border_width:, :, :] = color  # bottom side

    return im
