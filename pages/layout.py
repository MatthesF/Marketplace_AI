import streamlit as st
import numpy as np
from PIL import Image
import os


def layout():
    st.set_page_config(layout="wide")

    st.title("Marketplace AI")

    st.write(
        "This is a demo of the Marketplace AI project. You can use this to create a description and name for your products to sell on facebook marketplace."
    )


def get_images():

    basepath = "assets/trial_products/"
    products = [i for i in os.listdir(basepath) if not i.startswith(".")]
    product = st.sidebar.selectbox("Select a product", products)
    image_files = [
        f
        for f in os.listdir(f"{basepath}/{product}/")
        if f.endswith((".png", ".jpg", ".jpeg"))
    ]
    images = [Image.open(f"{basepath}/{product}/{file}") for file in image_files]
    # rotate image 90 degrees
    images = [image.rotate(-90) for image in images]
    # crop black borders
    images = [image.crop(image.getbbox()) for image in images]
    return image_files, images


def path2title(path):
    return path.replace("_", " ").split(".")[0].title()


if __name__ == "__main__":
    out_path = "assets/model_output_examples/"

    # select from dropdown
    options = os.listdir(out_path)
    selected_option = st.sidebar.selectbox(
        "Select an option", options, format_func=path2title
    )
    parsed_final_report = np.load(out_path + selected_option, allow_pickle=True)[
        "arr_0"
    ].item()
    image_files, images = get_images()

    cols = st.columns((5, 3))
    with cols[0]:

        info_dict = {
            "title": "Medium Dark Blue Ceramic Teapot with Metal Infuser",
            "description": "This medium-sized teapot is perfect for tea enthusiasts. Made from high-quality ceramic or porcelain, it comes in a stylish dark blue color. The teapot features a metal handle and an infuser, making it both functional and modern. Ideal for brewing your favorite teas, it is in good condition with no visible damage.",
            "category": "Home & Kitchen",
            "price": "unknown",
            "currency": "unknown",
            "condition": "good",
            "location": "unknown",
            "brand": "unknown",
            "model": "unknown",
            "color": "Dark Blue",
            "size": "Medium",
            "material": "Ceramic or Porcelain",
        }
        im_dict = {
            "quality": "high",
            "discard": False,
            "note": "The images are clear and well-lit, showing the teapot from different angles.",
        }
        question_for_user = "What is the price you would like to set for this teapot, and in which currency? Additionally, do you have the brand or model information?"

        
        info_dict
        st.write(f"**Image Quality**: {im_dict['quality']}")
        st.write(f"**Discard Images**: {im_dict['discard']}")
        st.write(f"**Note**: {im_dict['note']}")
        st.write(f"**Question for User**: {question_for_user}")
        


    with cols[1]:
        display_image_field = st.empty()
        display_image_field.image(images[0])

        sub_cols_images = st.columns(len(image_files))
        for i, sub_col in enumerate(sub_cols_images):
            with sub_col:
                # if st.button(f"Image {i+1}"):  # this was an attempt at make the images switchable
                #     display_image_field.image(images[i])  # however, the main image is most important, so perhaps we should not allow switching
                st.image(images[i])
