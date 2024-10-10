import streamlit as st
import matplotlib.pyplot as plt


im_path = 'assets/flow_v0.png'

im = plt.imread(im_path)

def add_colored_border(im, border_width=20, color=(.99, .0, .0, 0.95)):
    """
    Adds a colored border to the image.
    
    Parameters:
    - im: The input image.
    - border_width: The width of the border.
    - color: A tuple representing the RGBA color of the border.
    """
    im[:,:border_width, :] = color  # left side
    im[:,-border_width:, :] = color  # right side
    im[:border_width,:, :] = color  # top side
    im[-border_width:,:, :] = color  # bottom side
    
    return im

im = add_colored_border(im)

st.image(im)