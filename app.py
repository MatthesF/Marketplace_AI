import streamlit as st
from PIL import Image
import numpy as np
from src.utils import encode_images
from src.openai_api import get_image_description
from src.agents import setup_agent

st.title("Second-Hand Product Listing Generator")

# File uploader
uploaded_files = st.file_uploader(
    "Choose image files",
    accept_multiple_files=True,
    type=["png", "jpg", "jpeg"]
)

# Sidebar options
with st.sidebar:
    offline = st.checkbox('Offline Mode', value=False)

# Display columns
cols = st.columns(2)

if uploaded_files:
    # Open images from uploaded files
    images = [Image.open(file) for file in uploaded_files]

    # Display images in the first column
    with cols[0]:
        for image in images:
            st.image(image)

    # Display descriptions and agent response in the second column
    with cols[1]:
        if not offline:
            # Get descriptions for images if online
            desc = get_image_description(images)
            np.savez('desc.npz', desc)  # Save descriptions
        else:
            # Load descriptions from saved file if offline
            desc = np.load('desc.npz', allow_pickle=True)
            desc = desc[desc.files[0]]

        # Display the descriptions
        st.write(desc.dict().get("content"))
