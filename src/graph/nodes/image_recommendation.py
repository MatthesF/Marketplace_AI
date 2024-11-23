from typing import Any, Dict
from graph.state import GraphState
import streamlit as st
from PIL import Image
from src.utils.image_processing import add_red_border

def image_recommendation(state: GraphState) -> Dict[str, Any]:

    st.session_state.recommendation = state["image_recommendation"]

    for i, uploaded_file in enumerate(st.session_state.uploaded_files):
        if str(i) in state["image_titles"]:
            uploaded_file.name = state["image_titles"][str(i)]

    for i in state["irrelevant_images"]:
        img = Image.open(st.session_state.uploaded_files[i])
        img_with_border = add_red_border(img)
        st.session_state.processed_images[i] = img_with_border
        
    ## some fuction to rerun streamlit site and get images or contiue
    return


