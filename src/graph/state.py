from typing import List, TypedDict
from PIL import Image


class GraphState(TypedDict):
    """
    Represents the state of the graph.

    Attributes:
        images: A list of images to be included.
        image_recommendation: Suggested images for the listing.
        image_description: Generated description for the listing.
        irrelevant_images: List of indices of images marked as irrelevant.
    """
    images: List[Image.Image]
    image_recommendation: str
    image_description: str
    irrelevant_images: List[int]
    image_titles: List[str]