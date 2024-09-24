import base64
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from .utils.image_processing import encode_image

def get_image_description(uploaded_files):
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
        {"type": "text", "text": "What’s in this image? You should focus on the object and its condition. If you recognize the brand name, please state it. Try to name Model of product and as much inforamtion as possible."}
    ] + image_contents

    # Create the message
    message = HumanMessage(content=message_content)

    # Invoke the model with the message
    return model.invoke([message])
