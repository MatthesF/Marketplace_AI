from typing import Any, Dict, List
from graph.state import GraphState
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.prompts import grading_prompt, desc_prompt
from chains import multi_modal_api
import streamlit as st

llm = ChatOpenAI(temperature=0)


class GradeImages(BaseModel):
    """
    Provides product recommendations, identifies images to remove, 
    and assigns titles to images.

    Note: Indexing for `images_to_remove` follows Python's zero-based indexing.
    """

    image_rec: str = Field(
        description="Indicates if the documents are relevant to the question. Expected values: 'yes' or 'no'."
    )

    image_titles: Dict[int, str] = Field(
        description="Dictionary mapping image indices to their titles. Uses Python's zero-based indexing"
    )

    irrelevant_images: List[int] = Field(
        description="List of indices of images to remove. Uses Python's zero-based indexing."
    )


def retrieve(state: GraphState) -> Dict[str, Any]:
    images = st.session_state.uploaded_files

    state["image_description"] = multi_modal_api(images, desc_prompt)

    structured_llm_grader = llm.with_structured_output(GradeImages)

    grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", grading_prompt),
        ("human", "Image descriptions: \n\n {state["image_description"]}"),
    ]
    )

    image_grader = grade_prompt | structured_llm_grader
    grading_result = image_grader.invoke()

    # Extract and return results
    return {
        "image_recommendation": grading_result.image_recommendation,
        "irrelevant_images": grading_result.irrelevant_images,
        "image_titles": grading_result.image_titles,
    }