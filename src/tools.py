import json
import streamlit as st
from PIL import Image
from langchain.agents import Tool
from .utils.image_processing import add_red_border

def recommendation(input_str: str) -> str:
    """
    Function that takes a JSON string as input, parses it to extract
    'removed_images' list, 'suggestions' string, and a "image_titles" dictionary of each image index with a brief description.
    It then performs the recommendation logic.
    """
    # Parse the input string as JSON
    input_data = json.loads(input_str.strip().strip("'"))
    removed_images = input_data.get('removed_images', [])
    st.session_state.recommendation = input_data.get('suggestions', '')
    image_titles = input_data.get('image_titles', {})

    # Initialize processed_images if not already done
    if 'processed_images' not in st.session_state:
        st.session_state.processed_images = [None] * len(st.session_state.uploaded_files)

    # Update image names based on recommendations
    for i, uploaded_file in enumerate(st.session_state.uploaded_files):
        if str(i) in image_titles:
            uploaded_file.name = image_titles[str(i)]
        
    # Add red borders to recommended images for removal
    for i in removed_images:
        img = Image.open(st.session_state.uploaded_files[i])
        img_with_border = add_red_border(img)
        st.session_state.processed_images[i] = img_with_border

    st.rerun()

    return "Recommendation processed."

recommendation_tool = Tool(
    name="recommendation",
    func=recommendation,
    description=recommendation.__doc__,
)
