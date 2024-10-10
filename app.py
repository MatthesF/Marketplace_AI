import streamlit as st
from PIL import Image, ImageDraw
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, MODEL_NAME
import json

# Streamlit setup
st.title("Second-Hand Product Listing Generator")

# File uploader
uploaded_files = st.file_uploader(
    "Choose image files",
    accept_multiple_files=True,
    type=["png", "jpg", "jpeg"]
)

# Function to add red border around an image
def add_red_border(image, border_width=10):
    """Adds a red border to the provided image."""
    width, height = image.size
    new_size = (width + 2 * border_width, height + 2 * border_width)
    bordered_image = Image.new('RGB', new_size, "red")
    bordered_image.paste(image, (border_width, border_width))
    return bordered_image

# Open and store images
if uploaded_files:
    images = [Image.open(file) for file in uploaded_files]
    cols = 3

    # Display images without modification initially
    for i in range(0, len(images), cols):
        cols_layout = st.columns(cols)
        for j in range(cols):
            if i + j < len(images):
                with cols_layout[j]:
                    st.image(images[i + j], use_column_width=True)

# Define the expected output schema using Pydantic
class RecommendationOutput(BaseModel):
    removed_images: list[int] = Field(description="List of zero-based indices of images to remove")
    suggestions: str = Field(description="Suggestions for additional images or angles")

# Create an output parser based on the schema
output_parser = PydanticOutputParser(pydantic_object=RecommendationOutput)


# Define the recommendation function
def recommendation(input_str: str) -> str:
    """
    Takes a JSON string as input, parses it to extract 'removed_images' and 'suggestions',
    modifies images based on 'removed_images' (adds red borders), and displays updated images in Streamlit.
    """
    try:
        # Parse the input string using the output parser
        parsed_output = output_parser.parse(input_str)
        removed_images = parsed_output.removed_images
        suggestions = parsed_output.suggestions
        st.write("Hey")

        # Add red border to images flagged for removal
        bordered_images = []
        for i, img in enumerate(images):
            if i in removed_images:
                img_with_border = add_red_border(img)
                bordered_images.append(img_with_border)
            else:
                bordered_images.append(img)

        

        # Display updated images with borders in Streamlit
        st.subheader("Updated Images (Red Border = Suggested for Removal):")
        for i in range(0, len(bordered_images), cols):
            cols_layout = st.columns(cols)
            for j in range(cols):
                if i + j < len(bordered_images):
                    with cols_layout[j]:
                        st.image(bordered_images[i + j], use_column_width=True)

        return f"Nothing has been implented so end chain here"
    except Exception as e:
        return f"Error parsing input: {e}"


def recommendation(input_str: str) -> str:
    """
    Function that takes a JSON string as input, parses it to extract
    'removed_images' list and 'suggestions' string, and performs the recommendation logic.
    """
    # Parse the input string as JSON
    input_data = json.loads(input_str.strip().strip("'"))
    removed_images = input_data.get('removed_images', [])
    suggestions = input_data.get('suggestions', '')
    
    # Implement  logic here
    
    return f"Logic is not implemented, so just end chain and dont call any new tools. {removed_images},{suggestions}"

# Create the Tool
recommendation_tool = Tool(
    name="recommendation",
    func=recommendation,
    description=recommendation.__doc__,
)

tools = [recommendation_tool]

agent_prompt = """
You are an AI agent tasked with evaluating a set of images for a second-hand item listing. 
You will determine if the set of images is sufficient to give potential buyers all the relevant information. 
If the image set is not sufficient, you will call a tool named 'recommendation' to:
- Provide a list of the index numbers of the images that should be removed (using zero-based indexing)
- Suggest additional angles or close-ups that should be included.

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

# Get the format instructions from the output parser
format_instructions = output_parser.get_format_instructions()

# Initialize the PromptTemplate
prompt = PromptTemplate(
    template=agent_prompt,
    input_variables=["description"],
    partial_variables={"format_instructions": format_instructions},
)

# Initialize the agent with the tools and the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, stop=["\nObservation", "Observation"], api_key=OPENAI_API_KEY)

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
)


desc_prompt = """
You are an AI agent designed to analyze and evaluate image sets provided for an online resale listing. Your first task is to determine the type of item in the images (e.g., a car, electronic device, furniture, clothing, collectible, etc.) and then extract as much relevant information as possible based on the nature of the item. This information may include identifying numbers, labels, condition, and other details important to a potential buyer. Use this understanding to tailor your analysis dynamically based on the specifics of the item.

Start by analyzing the set of images together to see if they collectively provide enough information for an informed buyer decision. Look for important perspectives such as front, back, sides, and any close-up images showing key features, wear, damage, or identifying marks. Ensure all critical angles for the item type are covered. If a particular perspective is missing, check if it’s implicitly covered by another image. Avoid recommending the removal of images that provide useful information indirectly.

Once the set evaluation is complete, proceed with a detailed image-by-image analysis. For each image, dynamically identify what is important based on the item type. For example, if it's an item that typically has a serial number, ensure that the number is visible. If the condition of the item is crucial to buyers, describe any visible damage or wear. Extract any relevant information such as labels, maker’s marks, visible wear, model numbers, or unique identifying features. Assess the quality of each image in terms of clarity, lighting, and focus. If an image is blurry or poorly lit, note its index using zero-based indexing, e.g., image 0, image 1, and explain why it needs replacement. If multiple images show the same detail, decide whether they are redundant or complementary and recommend whether to keep, remove, or replace them based on their usefulness. Identify any missing images that would be useful for the specific item type. For example, if it's an item where buyers expect to see certain angles or features, such as a close-up of a label or damage, suggest adding those images. If these details are optional and not necessary for a full understanding of the item, such as serial numbers on items where they are not relevant, recognize them as such.

Finally, provide a recommendation on whether the image set is sufficient for a complete listing. Suggest which images, if any, need to be added, replaced, or removed, and provide a clear explanation for each recommendation. Ensure that your suggestions improve the listing without overwhelming the seller with unnecessary requests. The goal is to maximize the buyer's understanding of the item while keeping the listing efficient and concise.
"""

import base64
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from src.utils.image_processing import encode_image

def multi_modal_api(uploaded_files,prompt):
    """
    Gets the description of the images from the OpenAI API.
    """

    model = ChatOpenAI(model=f"{MODEL_NAME}",api_key=OPENAI_API_KEY)

    image_contents = []

    # Convert each uploaded image to base64 string
    for uploaded_file in uploaded_files:
        image_base64 = encode_image(uploaded_file)
        image_contents.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image_base64}"}
        })

    # Create the HumanMessage content
    message_content = [
        {"type": "text", "text": prompt}
    ] + image_contents

    # Create the message
    message = HumanMessage(content=message_content)

    # Invoke the model with the message
    return model.invoke([message])

if st.button("genreate"):
    images = [Image.open(file) for file in uploaded_files]

    desc = multi_modal_api(images,desc_prompt)

    st.write(desc)

    # Format the prompt with the description
    formatted_prompt = prompt.format_prompt(description=desc.content)

    st.write("response")
    response = agent(formatted_prompt.to_string())

# Print the response in Streamlit
    st.write(response)
