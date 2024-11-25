from typing import List, TypedDict
from PIL import Image


class GraphState(TypedDict):
    """
    Represents the state of the graph.

    Attributes:
        images: A list of images to be included.
        image_rec: Suggested images for the listing.
        image_description: Generated description for the listing.
        irrelevant_images: List of indices of images marked as irrelevant.
        image_titles: List of titles for the images.
        user_next_step: The next step the user should take.
    """
    images: List[Image.Image]
    image_rec: str
    recommendation_history: List[str]
    image_description: str
    irrelevant_images: List[int]
    image_titles: List[str]
    user_next_step: str