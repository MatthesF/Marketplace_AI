import streamlit as st
from PIL import Image, ImageDraw
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from src.config import OPENAI_API_KEY, MODEL_NAME
import json
import gc


# Streamlit setup
st.title("Second-Hand Product Listing Generator")

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


# Function to add red border around an image
def add_red_border(image, border_width=10):
    """Adds a red border to the provided image."""
    width, height = image.size
    new_size = (width + 2 * border_width, height + 2 * border_width)
    bordered_image = Image.new("RGB", new_size, "red")
    bordered_image.paste(image, (border_width, border_width))
    return bordered_image


if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 1
if "processed_images" not in st.session_state:
    st.session_state.processed_images = []
if "recommendation" not in st.session_state:
    st.session_state.recommendation = ""


# Sidebar file uploader with a dynamic key
# Sidebar file uploader with a dynamic key
with st.sidebar:
    uploaded_files = st.file_uploader(
        "Choose image files",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"],
        key=st.session_state.uploader_key,
    )

    # Add new files to session state if they haven't been added
    if uploaded_files:
        for file in uploaded_files:
            # Check for duplicates using file_id instead of name
            if file.file_id not in [
                existing.file_id for existing in st.session_state.uploaded_files
            ]:
                st.session_state.uploaded_files.append(file)

# Cache images for consistent display and manage state
cached_images = [Image.open(file) for file in st.session_state.uploaded_files]
# Display images with remove option outside the sidebar
st.subheader("Uploaded Images")
cols = 3  # Number of columns to display images in a grid

# Display images in a grid with remove buttons
if st.session_state.recommendation:
    st.write(st.session_state.recommendation)


for i in range(0, len(cached_images), cols):
    cols_layout = st.columns(cols)
    for j in range(cols):
        if i + j < len(cached_images):
            file_index = i + j
            with cols_layout[j]:
                # Show processed image if available, otherwise show original
                display_image = (
                    st.session_state.processed_images[file_index]
                    if st.session_state.processed_images
                    and st.session_state.processed_images[file_index] is not None
                    else cached_images[file_index]
                )
                st.image(
                    display_image,
                    use_column_width=True,
                    caption=st.session_state.uploaded_files[file_index].name,
                )

                # Remove button to delete the file from session state
                if st.button(
                    f"Remove: {st.session_state.uploaded_files[file_index].name}",
                    key=f"remove_{file_index}",
                ):
                    try:
                        # Get the file_id of the file to remove
                        file_id_to_remove = st.session_state.uploaded_files[
                            file_index
                        ].file_id

                        # Remove all instances of this file_id
                        st.session_state.uploaded_files = [
                            f
                            for f in st.session_state.uploaded_files
                            if f.file_id != file_id_to_remove
                        ]

                        # Increment the uploader key
                        st.session_state.uploader_key += 1

                        # Rerun the app
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error removing image: {str(e)}")


def recommendation(input_str: str) -> str:
    """
    Function that takes a JSON string as input, parses it to extract
    'removed_images' list, 'suggestions' string, and a "image_titles" dictionary of each image index with a brief description.
    It then performs the recommendation logic.
    """
    # Parse the input string as JSON
    input_data = json.loads(input_str.strip().strip("'"))
    removed_images = input_data.get("removed_images", [])
    st.session_state.recommendation = input_data.get("suggestions", "")
    image_titles = input_data.get("image_titles", {})

    # Update image names based on recommendations
    for i, uploaded_file in enumerate(st.session_state.uploaded_files):
        if str(i) in image_titles:
            uploaded_file.name = image_titles[str(i)]

    # Add red borders to recommended images for removal
    for i, img in enumerate(cached_images):
        st.session_state.uploaded_files[i].name = image_titles[str(i)]
        if i in removed_images:
            img_with_border = add_red_border(img)
            cached_images[i] = img_with_border
            st.session_state.processed_images = [None] * len(cached_images)
            st.session_state.processed_images[i] = img_with_border

    st.rerun()

    return f"Logic is not implemented, so just end chain and dont call any new tools. {removed_images},{suggestions}"


recommendation_tool = Tool(
    name="recommendation",
    func=recommendation,
    description=recommendation.__doc__,
)

tools = [recommendation_tool]

agent_prompt = """
You are an AI agent tasked with evaluating a set of images for a second-hand item listing. You will determine if the set of images is sufficient to give potential buyers all the relevant information. If the image set is not sufficient, you will call a tool named 'recommendation' to:
- Provide a list of the index numbers of the images that should be removed (using zero-based indexing).
- Suggest additional angles or close-ups that should be included.
- Provide a short name with each index of the images thats describes.

There can only be one product per listing. If there are multiple products in the images, select the one that is most likely to be the intended item for the listing.

You must also analyze the images based on the item description. If no specific angle is mentioned in the description, infer what is important for the item (e.g., model numbers, labels, damage, etc.).

Example:

Given the item description: "A used smartphone with visible scratches on the screen. Model number iPhone 12."

Images might include:
- Front view (clear)
- Back view (blurred)
- Side view (redundant with another image)

Your analysis would be:
- Remove the side view (index 2) as it is redundant.
- Recommend adding a close-up of the scratches and the model number on the back.

Use this logic when analyzing any image set.

Here is the item description: {description}
"""


# Initialize the PromptTemplate
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
    stop=["\nObservation", "Observation"],
    api_key=OPENAI_API_KEY,
)


# Create the prompt for the agent
prompt = PromptTemplate.from_template(template=agent_prompt).partial(
    tools=tools,
    tool_names=", ".join([t.name for t in tools]),
)

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
)


desc_prompt = """
You are an AI agent designed to analyze and evaluate image sets provided for an online resale listing. Your first task is to determine the type of item in the images (e.g., a car, electronic device, furniture, clothing, collectible, etc.) and then extract as much relevant information as possible based on the nature of the item. This information may include identifying numbers, labels, condition, and other details important to a potential buyer. Use this understanding to tailor your analysis dynamically based on the specifics of the item.

Start by analyzing the set of images together to see if they collectively provide enough information for an informed buyer decision. Look for important perspectives such as front, back, sides, and any close-up images showing key features, wear, damage, or identifying marks. Ensure all critical angles for the item type are covered. If a particular perspective is missing, check if it’s implicitly covered by another image. Avoid recommending the removal of images that provide useful information indirectly.

Once the set evaluation is complete, proceed with a detailed image-by-image analysis. For each image, dynamically identify what is important based on the item type. For example, if it's an item that typically has a serial number, ensure that the number is visible. If the condition of the item is crucial to buyers, describe any visible damage or wear. Extract any relevant information such as labels, maker’s marks, visible wear, model numbers, or unique identifying features. Assess the quality of each image in terms of clarity, lighting, and focus. If an image is blurry or poorly lit, note its index using zero-based indexing, e.g., image 0, image 1, and explain why it needs replacement. If multiple images show the same detail, decide whether they are redundant or complementary and recommend whether to keep, remove, or replace them based on their usefulness. Identify any missing images that would be useful for the specific item type. For example, if it's an item where buyers expect to see certain angles or features, such as a close-up of a label or damage, suggest adding those images. If these details are optional and not necessary for a full understanding of the item, such as serial numbers on items where they are not relevant, recognize them as such. There can only be one product per listing. If there are multiple products in the images, select the one that is most likely to be the intended item for the listing.

Finally, provide a recommendation on whether the image set is sufficient for a complete listing. Suggest which images, if any, need to be added, replaced, or removed, and provide a clear explanation for each recommendation. Ensure that your suggestions improve the listing without overwhelming the seller with unnecessary requests. The goal is to maximize the buyer's understanding of the item while keeping the listing efficient and concise.
"""

import base64
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from src.config import OPENAI_API_KEY, MODEL_NAME
from src.utils.image_processing import encode_image


def multi_modal_api(uploaded_files, prompt):
    """
    Gets the description of the images from the OpenAI API.
    """

    model = ChatOpenAI(model=f"{MODEL_NAME}", api_key=OPENAI_API_KEY)

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


if st.button("Generate"):
    images = [Image.open(file) for file in uploaded_files]

    desc = multi_modal_api(images, desc_prompt)

    # Format the prompt with the description
    formatted_prompt = prompt.format_prompt(description=desc.content)

    response = agent(formatted_prompt.to_string())
