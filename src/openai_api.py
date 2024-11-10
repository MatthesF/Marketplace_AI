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


import ollama

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

