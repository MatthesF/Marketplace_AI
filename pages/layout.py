import streamlit as st
import numpy as np
from PIL import Image
import os
import json


def setup_layout():
    """
    Sets up the page configuration and sidebar for the Streamlit app.
    """
    st.set_page_config(layout="wide")
    st.sidebar.title("Marketplace AI")
    st.sidebar.write(
        "This is a demo of the Marketplace AI project. You can use this to create a description and name for your products to sell on Facebook Marketplace."
    )


def load_data(basepath, product):
    """
    Loads data related to the selected product, including images, description, image quality, and question.

    Args:
        basepath (str): The base path where product data is stored.
        product (str): The selected product.

    Returns:
        dict: A dictionary containing product data.
    """
    # Load images
    image_files = [
        f
        for f in os.listdir(f"{basepath}/{product}/")
        if f.endswith((".png", ".jpg", ".jpeg"))
    ]
    images = [Image.open(f"{basepath}/{product}/{file}") for file in image_files]

    # Rotate and crop images (if needed)
    images = [
        image.rotate(0) for image in images
    ]  # No actual rotation applied; adjust or remove if unnecessary
    images = [image.crop(image.getbbox()) for image in images]

    # Load other product data
    with open(f"{basepath}/{product}/description.json", "r") as f:
        description = json.load(f)
    with open(f"{basepath}/{product}/image_quality.json", "r") as f:
        image_quality = json.load(f)
    with open(f"{basepath}/{product}/question.txt", "r") as f:
        question = f.read()

    return {
        "description": description,
        "image_quality": image_quality,
        "question": question,
        "image_files": image_files,
        "images": images,
    }


def display_product_data(data):
    """
    Displays product data in the Streamlit app, including images, descriptions, and additional information.

    Args:
        data (dict): A dictionary containing product data.
    """
    # Layout for product description and details
    cols = st.columns((5, 3))
    with cols[0]:
        st.markdown(f"""### {data['description']['title']}""")
        st.write(data["description"]["description"])

        # Split the remaining description items into two columns
        description_items = list(data["description"].items())[2:]
        col1_items = dict(description_items[: len(description_items) // 2])
        col2_items = dict(description_items[len(description_items) // 2 :])
        col1, col2 = st.columns(2)
        col1.write(col1_items)
        col2.write(col2_items)

        # Display image quality information
        st.write("Image Quality")
        try:
            # assert False
            # data["image_quality"] can be a nested dict
            import pandas as pd

            tmp = data["image_quality"]["images"]
            tmp = {i: tmp[i] for i in range(len(tmp))}
            df = pd.DataFrame(tmp).T
            st.dataframe(df)
        except:
            st.write(data["image_quality"])
        # Display question
        st.write("Question")
        st.write(data["question"])

    # Layout for displaying images
    with cols[1]:
        display_image_field = st.empty()
        display_image_field.image(data["images"][0])

        # Display thumbnails of all images
        sub_cols_images = st.columns(len(data["image_files"]))
        for i, sub_col in enumerate(sub_cols_images):
            with sub_col:
                st.image(data["images"][i], use_column_width=True)


if __name__ == "__main__":
    setup_layout()

    basepath = "assets/model_outputs/"
    products = [i for i in os.listdir(basepath) if not i.startswith(".")]
    selected_product = st.sidebar.selectbox("Select a product", products)

    if selected_product:
        product_data = load_data(basepath, selected_product)
        display_product_data(product_data)
