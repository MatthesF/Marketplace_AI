from typing import List, TypedDict
from PIL import Image
from io import BytesIO
import base64


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


class GraphState(TypedDict):
    """
    Represents the state of the graph with serializable images.

    Attributes:
        images: A list of base64-encoded strings representing images.
        image_rec: Suggested images for the listing.
        image_description: Generated description for the listing.
        irrelevant_images: List of indices of images marked as irrelevant.
        image_titles: List of titles for the images.
        user_next_step: The next step the user should take.
    """
    images: List[str] 
    image_rec: str
    recommendation_history: List[str]
    image_description: str
    irrelevant_images: List[int]
    image_titles: List[str]
    user_next_step: str
