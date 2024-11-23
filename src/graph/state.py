from typing import List, TypedDict


class GraphState(TypedDict):
    """
    Represents the state of the graph.

    Attributes:
        question: The question or input for the graph.
        image_recommendation: Suggested images for the listing.
        image_description: Generated description for the listing.
        irrelevant_images: List of indices of images marked as irrelevant.
    """

    question: str
    image_recommendation: str
    image_description: str
    irrelevant_images: List[int]