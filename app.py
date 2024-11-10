import streamlit as st
from PIL import Image
from src.utils import initialize_session_state, display_images_with_remove_option
from src.prompts import agent_prompt, desc_prompt
from src.openai_api import multi_modal_api
from src.agents import initialize_new_agent
from config import OPENAI_API_KEY

# Streamlit setup
st.title("Second-Hand Product Listing Generator")

# Initialize session state
initialize_session_state()

# Add a language selection dropdown in the sidebar
language = st.sidebar.selectbox("Choose your language:", ["English", "Danish", "Spanish"])

# Sidebar file uploader with a dynamic key
with st.sidebar:
    uploaded_files = st.file_uploader(
        "Choose image files",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"],
        key=st.session_state.uploader_key
    )

    # Add new files to session state if they haven't been added
    if uploaded_files:
        for file in uploaded_files:
            # Check for duplicates using file_id instead of name
            if file.file_id not in [existing.file_id for existing in st.session_state.uploaded_files]:
                st.session_state.uploaded_files.append(file)
                st.session_state.processed_images.append(None)  # Append None for each new file


# Cache images for consistent display
cached_images = [Image.open(file) for file in st.session_state.uploaded_files]
# Display images with remove option
display_images_with_remove_option(cached_images)



# Generate recommendation when button is clicked
if st.button("Generate"):
    images = [Image.open(file) for file in st.session_state.uploaded_files]
    desc = multi_modal_api(images, desc_prompt)

    # Initialize the agent
    agent,prompt = initialize_new_agent()

    formatted_prompt = prompt.format(description=desc.content, language=language)

    response = agent(formatted_prompt)
    st.write(response)
