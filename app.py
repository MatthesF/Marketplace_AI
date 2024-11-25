import streamlit as st
from PIL import Image
from src.utils import initialize_session_state, display_images_with_remove_option
from config import OPENAI_API_KEY
from src.graph.graph import graph
from src.utils.image_processing import add_red_border

# Streamlit setup
st.title("Second-Hand Product Listing Generator")

# Initialize session state
initialize_session_state()

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

button_placeholder = st.empty()

with button_placeholder:
    if st.session_state.which_run == "first":

        if st.button("Generate"):

            thread = {"configurable": {"thread_id": "777"}}
            initial_input = {"images": [Image.open(file) for file in st.session_state.uploaded_files]}


            for event in graph.stream(initial_input, thread, stream_mode="values"):
                print(event)

            for i, uploaded_file in enumerate(st.session_state.uploaded_files):
                if str(i) in graph.get_state(thread).values["image_titles"]:
                    uploaded_file.name = graph.get_state(thread).values["image_titles"][str(i)]  

            for i in graph.get_state(thread).values["irrelevant_images"]:
                img = Image.open(st.session_state.uploaded_files[i])
                img_with_border = add_red_border(img)
                st.session_state.processed_images[i] = img_with_border
            

            st.session_state.which_run = "image_choice"
            st.session_state.recommendation = graph.get_state(thread).values["image_rec"]

            st.rerun()

    if st.session_state.which_run == "image_choice":

        if st.button("Regenerate"):
            st.session_state.which_run = "regenerate"
            graph.update_state(thread, {"images": cached_images, "user_next_step": "regenerate"}, as_node="human_feedback")

        if st.button("Continue"):
            st.session_state.which_run = "sufficient"
            graph.update_state(thread, {"images": cached_images, "user_next_step": "sufficient"}, as_node="human_feedback")


