from typing import Any, Dict, List
from src.graph.state import GraphState
from pydantic import BaseModel, Field, Json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.prompts import grading_prompt, desc_prompt
from src.graph.chains.multi_modal_gen import multi_modal_api
import streamlit as st
from src.config import MODEL_NAME

llm = ChatOpenAI(temperature=0, model=MODEL_NAME)


class GradeImages(BaseModel):
    """
    Provides product recommendations, identifies images to remove, 
    and assigns titles to images.

    Note: Indexing for `images_to_remove` follows Python's zero-based indexing.
    """

    image_rec: str = Field(
        description="Gives user a recommendation on which image to change, remove, or keep."
    )

    image_titles: Json = Field(
        description="Dictionary mapping each image index as a key to the image title as a value. Uses Python's zero-based indexing."
    )

    irrelevant_images: List[int] = Field(
        description="List of indices of images to remove. Uses Python's zero-based indexing."
    )


def image_choice(state: GraphState) -> Dict[str, Any]:

    state["image_description"] = multi_modal_api(state["images"], desc_prompt)

    st.write(state["image_description"])

    structured_llm_grader = llm.with_structured_output(GradeImages)

    grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", grading_prompt),
        ("human", f"Image descriptions: {{image_description}}"),
    ]
    )

    image_grader = grade_prompt | structured_llm_grader

    grading_result = image_grader.invoke({"image_description": state["image_description"].content})

    # Extract and return results
    return {
        "image_recommendation": grading_result.image_rec,
        "irrelevant_images": grading_result.irrelevant_images,
        "image_titles": grading_result.image_titles,
    }