import os
import clip
from PIL import Image
import torch
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.gridspec as gridspec
import streamlit as st
import numpy as np
# get file paths

# set page config wide
st.set_page_config(layout="wide", page_title="Image splitter")


def get_clip_embeddings(im_paths):

    # make clip embeddings

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # preprocess images
    ims_processed = [preprocess(Image.open(i)).unsqueeze(0).to(device) for i in im_paths]
    ims_processed = torch.cat(ims_processed)
    # get embeddings
    ims_emb = model.encode_image(ims_processed)
    return ims_emb

def get_cosine_similarity(X):
    # cosine similarity
    cos_sim = cosine_similarity(X.cpu().detach().numpy())
    return cos_sim

def show_image_similarity(im_paths, cos_sim):
    # gridspec plot
    fig = plt.figure(figsize=(8, 8))
    gs = gridspec.GridSpec(1+len(im_paths), 1+len(im_paths))
    sim_ax = fig.add_subplot(gs[1:, 1:])
    sim_ax.imshow(cos_sim, aspect='equal', cmap='RdBu')
    sim_ax.set_xticks([])
    sim_ax.set_yticks([])
    # insert text labels from sim
    for i in range(len(im_paths)):
        for j in range(len(im_paths)):
            sim_ax.text(j, i, f'{cos_sim[i,j]:.2f}', ha='center', va='center')

    im_axes = []
    for i in range(len(im_paths)):

        im_axes.append(fig.add_subplot(gs[0, 1+i]))
        im_axes[-1].imshow(Image.open(im_paths[i]))
        im_axes[-1].axis('off')
        im_axes.append(fig.add_subplot(gs[1+i, 0]))
        im_axes[-1].imshow(Image.open(im_paths[i]))
        im_axes[-1].axis('off')
    return fig

def get_groups(im_paths, cos_sim, lenience = .1):
    # for each image, we want to find likely matches
    grouped_to = {}
    for i in range(len(im_paths)):
        most_similar = cos_sim[i].argsort()[-2]
        likeness_of_most_similar = cos_sim[i, most_similar]
        # likeness_of_most_similar

        # likely matches
        # likely_matches = cos_sim[i].argwhere(cos_sim[i] > likeness_of_most_similar-lenience)
        likely_matches = np.argwhere(cos_sim[i] > likeness_of_most_similar-lenience)
        likely_matches_idx = cos_sim[i][likely_matches]
        # remove self
        # likely_matches = likely_matches[likely_matches != i]
        grouped_to[i] = tuple(zip(likely_matches_idx, likely_matches, ))


    # grouped_to

    # group
    groups = {}
    counter = 0
    seen = []
    for i in grouped_to:
        # st.write(i)
        # st.write(grouped_to[i])
        if i in seen:
            continue
        indicies = [k[1].item() for k in grouped_to[i]]
        # indicies
        indicies = [ind for ind in indicies if ind not in seen]
        groups[counter] = indicies
        seen += indicies
        counter += 1

    return groups


'# Image Grouping with CLIP'

base_path = 'assets/many_products/'
im_paths = [base_path+i for i in os.listdir(base_path) if i.endswith('.png')]
ims_emb = get_clip_embeddings(im_paths)
cos_sim = get_cosine_similarity(ims_emb)
fig = show_image_similarity(im_paths, cos_sim)


cols = st.columns((2,3,1))
with cols[0]: 
    st.write('#### Algorithm description')
    st.write("""When multiple images are uploaded, the CLIP model is used to encode the images. Images are then compared using cosine similarity. High similarity scores are grouped together.
             
We use a threshhold for grouping. We consider the nearest neighbour to be the most similar image. and then group all images with that score - lenience.""")

    lenience = st.slider('Lenience', min_value=0.0, max_value=.5, value=0.07, step=0.01)

    st.write('#### Image data')
    with st.expander('Image paths'):
        st.write(im_paths)

    with st.expander('Image embeddings', expanded=True):
        st.write(ims_emb)

    with st.expander('Cosine similarity'):
        st.write(cos_sim)


with cols[1]:
    st.write('#### Cosine similarity')
    st.pyplot(fig)
groups = get_groups(im_paths, cos_sim, lenience)
with cols[2]: 
    st.write('#### Groups')
    st.write(groups)

'---'

# show by group
for group in groups:
    st.write(f'### Group {group}, with {len(groups[group])} images')

    cols = st.columns(len(groups[group]))
    # for i in groups[group]:
    #     st.image(im_paths[i], width=200)
    for i, col in zip(groups[group], cols):
        col.image(im_paths[i], width=200)
    '---'