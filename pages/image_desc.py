import os
import numpy as np
import streamlit as st
from PIL import Image
import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

from config import OPENAI_API_KEY, MODEL_NAME
from src.utils.image_processing import encode_image


# Define your desired data structure.
class Suggestion(BaseModel):
    index: int = Field(description="index of the image")
    suggested_name: str = Field(description="suggested name for the image")
    keep_or_rid: str = Field(description="whether to keep or remove the image")


class Final_report(BaseModel):
    title: str = Field(description="title of the product")
    description: str = Field(description="description of the product")
    category: str = Field(description="category of the product")
    price: float = Field(description="price of the product")
    currency: str = Field(description="currency of the product")
    condition: str = Field(description="condition of the product")
    location: str = Field(description="location of the product")
    brand: str = Field(description="brand of the product")
    model: str = Field(description="model of the product")


def multi_modal_api(uploaded_files, prompt):
    """
    Gets the description of the images from the OpenAI API.
    """
    model = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY)

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

    # Create the HumanMessage content
    message_content = [{"type": "text", "text": prompt}] + image_contents

    # Create the message
    message = HumanMessage(content=message_content)

    # Invoke the model with the message
    return model.invoke([message])


def openai_api(text, prompt):
    model = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY)

    message_content = [{"type": "text", "text": prompt}, {"type": "text", "text": text}]

    # Create the message
    message = HumanMessage(content=message_content)

    return model.invoke([message])


# Streamlit file uploader function
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
                            st.image(image, use_column_width=True)
                            image_captions.append(st.empty())

            return uploaded_files, images, image_captions

    return False, [], []


# Notebook file uploader function
def notebook_file_uploader():
    # product = 'bluetooth_sound_reciever_small'
    product = "tea_pot"
    image_files = [
        f
        for f in os.listdir(f"trial_products/{product}/")
        if f.endswith((".png", ".jpg", ".jpeg"))
    ]
    images = [Image.open(f"trial_products/{product}/{file}") for file in image_files]
    return image_files, images, None


# Load prompts from JSON file
def load_prompts(path="prompts.json", verbose=False):
    with open(path, "r") as f:
        prompts = json.load(f)

    if verbose:
        for key, value in prompts.items():
            print(f"{key} :\t {value[:50]}")

    return prompts


def title2path(title):
    return title.replace(" ", "_")


uploaded_files, images, image_captions = streamlit_file_uploader()
if uploaded_files:
    # Main logic
    prompts = load_prompts(verbose=True)

    # Chain execution
    response_description = multi_modal_api(images, prompts["image description"])
    response_name_extraction = openai_api(
        response_description.content, prompts["image name extraction"]
    )

    # Parsing the output
    suggestion_parser = JsonOutputParser(pydantic_object=Suggestion)
    parsed_output = suggestion_parser.parse(response_name_extraction.content)

    # the final report is made by taking the response_description and asking for output to match facebook marketplace format
    # here we could use an agent to ask the user when it need information.
    final_prompt = prompts["final report"]

    final_report = openai_api(response_description.content, final_prompt)

    print(final_report.content)

    final_report_parser = JsonOutputParser(pydantic_object=Final_report)
    parsed_final_report = final_report_parser.parse(final_report.content)
    print(parsed_final_report)

    title2path(parsed_final_report["title"])

    parsed_final_report

    out_path = "model_output_examples/"
    np.savez(
        out_path + title2path(parsed_final_report["title"]) + ".npz",
        parsed_final_report,
    )
