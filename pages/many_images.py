import streamlit as st
from PIL import Image
from langchain_openai import ChatOpenAI
from src.utils.image_processing import encode_image
import os
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
load_dotenv()

def streamlit_file_uploader(show_images=True):
    with st.sidebar:
        uploaded_files = st.file_uploader(
            "Choose image files",
            accept_multiple_files=True,
            type=["png", "jpg", "jpeg"],
        )

        images = []
        if uploaded_files and show_images:
            cols = 3
            image_captions = []
            for i in range(0, len(uploaded_files), cols):
                cols_layout = st.columns(cols)
                for j in range(cols):
                    if i + j < len(uploaded_files):
                        with cols_layout[j]:
                            image = Image.open(uploaded_files[i + j])
                            images.append(image)
                            st.image(image, use_container_width=True)
                            image_captions.append(st.empty())

            return uploaded_files, images, image_captions

    return False, [], []



def get_image_contents(uploaded_files):
    image_contents = []

    # Convert each uploaded image to base64 string
    for uploaded_file in uploaded_files:
        image_base64 = encode_image(uploaded_file)
        image_contents.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_base64}"},
            }
        )

    return image_contents


# assert False
def multi_modal_prompt(prompt):
    """
    Makes a multimodal prompt with text and images
    """
    # Create the HumanMessage content
    message_content = [{"type": "text", "text": prompt}] + image_contents

    return message_content

def get_image_analysis(prompt):
    """
    Prompt-guided image analysis. Supply a prompt and get the analysis of the image. This function gets the images by itself. All you have to do is provide the prompt. And you recieve a string with the analysis of the image.
    """
    message_content = multi_modal_prompt(prompt)

    # Create the message
    message = HumanMessage(content=message_content)

    # Invoke the model with the message
    return model.invoke([message])


if __name__ == "__main__":
    
    # uploaded_files, images, _ = notebook_file_uploader()
    uploaded_files, images, _ = streamlit_file_uploader()
    if not uploaded_files:
        st.stop()
    image_contents = get_image_contents(images)
    model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
    # print(image_contents)

    prompt = "You will be given many images. You should split the by product."

    # invoke model
    response = get_image_analysis(prompt)
    st.write(response)