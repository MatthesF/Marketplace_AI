import base64
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from src.config import OPENAI_API_KEY, MODEL_NAME
from src.utils.image_processing import encode_image
from pydantic import BaseModel, Field, Json
import ollama

class ImageContent(BaseModel):
    """
    Provides product recommendations, identifies images to remove, 
    and assigns titles to images.

    Note: Indexing for `images_to_remove` follows Python's zero-based indexing.
    """


    image_descriptions: Json = Field(
        description= """A stringified JSON object where each key is a zero-based image index (e.g., '0', '1') and each value is a concise analysis of the image. 
            For each image, provide a structured description with the following details: 
            1. **Content:** A brief description of the main subject and notable elements in the image. 
            2. **Important Features:** Key features of the subject, such as condition, visibility, or other notable aspects relevant to its intended use. 
            3. **Clarity and Lighting:** An assessment of the image's quality, including focus, clarity, and lighting conditions, noting any factors affecting visibility. 
            4. **Relevance:** An evaluation of the image's relevance to its purpose or context, such as whether it sufficiently represents the subject or captures critical details. 
            5. **Model or Identifier Suggestions:** If applicable, suggest the model, make, or specific identifier of the subject (e.g., vehicle make/model or product), based on visual cues. 
            6. **Overall Quality:** A summary of the overall quality of the image with any suggestions for improvement. 
            7. **Angle of Photo:** An analysis of the angle from which the photo was taken and its impact on the image's effectiveness.
            8. **Color Accuracy:** An evaluation of the color accuracy in the image, noting any discrepancies or enhancements.
            9. **Composition:** An assessment of the image's composition, including the arrangement of elements and balance within the frame.
            Ensure the output format is strictly a **stringified JSON** object, where each image index is mapped to a structured analysis like:
            `{"0": "Content: ... \\n Important Features: ... \\n Clarity and Lighting: ... \\n Relevance: ... \\n Model or Identifier Suggestions: ... \\n Overall Quality: ... \\n Angle of Photo: ... \\n Color Accuracy: ... \\n Composition: ..."}`."""
    )


    collection_description: str = Field(
        description="A detailed description of the collection of images, including the overall theme, notable elements, and any common characteristics among the images."
    )

    initial_recommendation: str = Field(
        description="An in-depth initial recommendation of what the user needs to add, remove, or change to improve the collection of images. This should include specific suggestions for enhancing the overall quality, relevance, and completeness of the images."
    )


def multi_modal_api(uploaded_files, prompt):
    """
    Generates a description of the images using the OpenAI API.
    """

    # Initialize the chat model with the specified model name and API key
    model = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY)

    # Prepare the structured output model
    structured_model_output = model.with_structured_output(ImageContent)

    # Initialize a list to hold the content blocks
    message_content = []

    # Add the text prompt as the first content block
    message_content.append({"type": "text", "text": prompt})

    # Process each uploaded image
    for uploaded_file in uploaded_files:
        # Encode the image to a base64 string
        image_base64 = encode_image(uploaded_file)
        # Create an image content block
        image_content_block = {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image_base64}"},
        }
        # Append the image content block to the message content
        message_content.append(image_content_block)

    # Create the HumanMessage with the list of content blocks
    message = HumanMessage(content=message_content)

    # Invoke the model with the message and return the structured output
    return structured_model_output.invoke([message])



def ollama_vision_api(image_path, prompt):
    """
    Gets the description of the image using the Ollama API.
    
    Args:
        image_path (str): Path to the image file
        prompt (str): Text prompt to send with the image
        
    Returns:
        dict: Response from the Ollama API
    """
    return ollama.chat(
        model='llama2-vision',  # Changed from llama3.2-vision as that's not a valid model name
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image_path]
        }]
    )

