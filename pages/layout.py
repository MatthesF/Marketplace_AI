

import streamlit as st
import numpy as np
from PIL import Image
import os

def layout():
    st.set_page_config(layout="wide")

    st.title('Marketplace AI')

    st.write('This is a demo of the Marketplace AI project. You can use this to create a description and name for your products to sell on facebook marketplace.')

def get_images():
    
    basepath = 'trial_products/'
    products = [i for i in os.listdir(basepath) if not i.startswith('.')]
    product = st.sidebar.selectbox("Select a product", products)
    image_files = [f for f in os.listdir(f'{basepath}/{product}/') if f.endswith(('.png', '.jpg', '.jpeg'))]
    images = [Image.open(f'{basepath}/{product}/{file}') for file in image_files]
    # rotate image 90 degrees
    images = [image.rotate(-90) for image in images]
    # crop black borders
    images = [image.crop(image.getbbox()) for image in images]
    return image_files, images

def path2title(path):
    return path.replace('_', ' ').split('.')[0].title()

if __name__ == '__main__':
    out_path = 'model_output_examples/'

    # select from dropdown
    options = os.listdir(out_path)
    selected_option = st.sidebar.selectbox("Select an option", options, format_func=path2title)
    parsed_final_report = np.load(out_path + selected_option, allow_pickle=True)['arr_0'].item()
    image_files, images = get_images()

    cols = st.columns((5,3))
    with cols[0]:
        st.write(f"## {parsed_final_report['title']}")
        st.write(f"{parsed_final_report['description']}")

        sub_cols_info = st.columns(2)
        with sub_cols_info[0]:
            st.write(f"**Price**: {parsed_final_report['price']} {parsed_final_report['currency']}")
            st.write(f"**Condition**: {parsed_final_report['condition']}")
            st.write(f"**Category**: {parsed_final_report['category']}")
            st.write(f"**Location**: {parsed_final_report['location']}")
        with sub_cols_info[1]:
            
            st.write(f"**Brand**: {parsed_final_report['brand']}")
            st.write(f"**Model**: {parsed_final_report['model']}")
            st.write(f"**Color**: {parsed_final_report['color']}")
            st.write(f"**Size**: {parsed_final_report['size']}")
            st.write(f"**Material**: {parsed_final_report['material']}")

    with cols[1]:
        display_image_field = st.empty()
        display_image_field.image(images[0])

        sub_cols_images = st.columns(len(image_files))
        for i, sub_col in enumerate(sub_cols_images):
            with sub_col:
                # if st.button(f"Image {i+1}"):  # this was an attempt at make the images switchable
                #     display_image_field.image(images[i])  # however, the main image is most important, so perhaps we should not allow switching
                st.image(images[i])
