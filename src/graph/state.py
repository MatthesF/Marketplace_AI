from typing import List, TypedDict
from PIL import Image
import operator

class GraphState(TypedDict):
    """
    Represents the state of the graph with serializable images.

    Attributes:
        images: A list of base64-encoded strings representing images.
        image_recommendation: Suggested images for the listing.
        image_description: Generated description for the listing.
        irrelevant_images: List of indices of images marked as irrelevant.
        image_titles: List of titles for the images.
        user_next_step: The next step the user should take.
    """
    images: List[str] 
    image_recommendation: str
    recommendation_history: List[operator.add]
    image_description: str
    irrelevant_images: List[int]
    image_titles: List[str]
    user_next_step: str

