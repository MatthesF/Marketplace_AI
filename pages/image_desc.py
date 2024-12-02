import getpass
import json
import os

import dotenv
import streamlit as st
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI

# from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor
from PIL import Image
from src.agents import AgentState, execute_tools_base, run_agent_base, should_continue
from src.parsers import get_parsers
from src.utils.image_processing import encode_image

from pages.layout import display_product_data, load_data

dotenv.load_dotenv()


def get_llm(type, **kwargs):
    if type == "azure":
        if "AZURE_OPENAI_API_KEY" not in os.environ:
            os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass(
                "Enter your AzureOpenAI API key: "
            )
        return AzureChatOpenAI(
            azure_deployment=kwargs.get("azure_deployment", "gpt-4o"),
            api_version=kwargs.get("api_version", "2023-06-01-preview"),
            temperature=kwargs.get("temperature", 0),
            max_tokens=kwargs.get("max_tokens", None),
            timeout=kwargs.get("timeout", None),
            max_retries=5,
            **kwargs,
        )
    elif type == "openai":
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=kwargs.get("model", "gpt-4o"),
            **kwargs,
        )
    elif type == "ollama":
        # llm = ChatOllama(model="llama3.2")  # other models include
        # llama3.1:8b
        # llama3.2
        # llama3.1:70b
        # fore more see: https://ollama.com/library
        kwargs["model"] = kwargs.get("model", "llama3.2")
        return ChatOllama(**kwargs)
    else:
        raise ValueError("Invalid LLM type")


def get_image_contents(uploaded_files):
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

    return image_contents


def notebook_file_uploader():
    # product = 'bluetooth_sound_reciever_small'
    product = "tea_pot_small"
    base_path = "assets/trial_products"
    image_files = [
        f
        for f in os.listdir(f"{base_path}/{product}/")
        if f.endswith((".png", ".jpg", ".jpeg"))
    ]
    print(image_files)
    images = [Image.open(f"{base_path}/{product}/{file}") for file in image_files]
    return image_files, images, None


# Streamlit file uploader function
def streamlit_file_uploader(show_images=True):
    with st.sidebar:
        uploaded_files = st.file_uploader(
            "Choose image files",
            accept_multiple_files=True,
            type=["png", "jpg", "jpeg"],
        )

        images = []
        if uploaded_files and show_images:
            cols = 3
            image_captions = []
            for i in range(0, len(uploaded_files), cols):
                cols_layout = st.columns(cols)
                for j in range(cols):
                    if i + j < len(uploaded_files):
                        with cols_layout[j]:
                            image = Image.open(uploaded_files[i + j])
                            images.append(image)
                            st.image(image, use_column_width=True)
                            image_captions.append(st.empty())

            return uploaded_files, images, image_captions

    return False, [], []


# uploaded_files, images, _ = notebook_file_uploader()
uploaded_files, images, _ = streamlit_file_uploader()
if not uploaded_files:
    st.stop()
image_contents = get_image_contents(images)
model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
# print(image_contents)


# assert False
def multi_modal_prompt(prompt):
    """
    Makes a multimodal prompt with text and images
    """
    # Create the HumanMessage content
    message_content = [{"type": "text", "text": prompt}] + image_contents

    return message_content


def get_image_analysis(prompt):
    """
    Prompt-guided image analysis. Supply a prompt and get the analysis of the image. This function gets the images by itself. All you have to do is provide the prompt. And you recieve a string with the analysis of the image.
    """
    message_content = multi_modal_prompt(prompt)

    # Create the message
    message = HumanMessage(content=message_content)

    # Invoke the model with the message
    return model.invoke([message])


def openai_api(text, prompt):
    model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    message_content = [{"type": "text", "text": prompt}, {"type": "text", "text": text}]

    # Create the message
    message = HumanMessage(content=message_content)

    return model.invoke([message])


def save_output(desc_dict, img_quality_dict, question, images):
    # save to assets/modle_outputs/{title_fname}/*.*
    title_fname = desc_dict["title"].replace(" ", "_").lower()

    if not os.path.exists(f"assets/model_outputs/{title_fname}"):
        os.makedirs(f"assets/model_outputs/{title_fname}")

    with open(f"assets/model_outputs/{title_fname}/description.json", "w") as f:
        json.dump(desc_dict, f)

    with open(f"assets/model_outputs/{title_fname}/image_quality.json", "w") as f:
        json.dump(img_quality_dict, f)

    with open(f"assets/model_outputs/{title_fname}/question.txt", "w") as f:
        f.write(question.content)

    for i, img in enumerate(images):
        img.save(f"assets/model_outputs/{title_fname}/image_{i}.png")

    return title_fname


llm = get_llm("openai")
# make workflow
if __name__ == "__main__":
    with st.sidebar:
        aux_user_data = {
            "currency": st.text_input("Currency", "DKK"),
            "language": st.text_input("Language", "en-US"),
            "region": st.text_input("Region", "US"),
            "urgency": st.text_input("Urgency", "high"),
            "tone_of_voice": st.text_input("Tone of Voice", "formal"),
            # 'api_key': st.text_input('API Key', os.getenv('OPENAI_API_KEY')),
            # 'model_selection': st.text_input('Model Selection', 'gpt-4o'),
            "profile_info": st.text_input("Profile Info", "location: US"),
        }

    # - **Currency**: The currency for price estimation.
    # - **Languages/Region**: Specify the language and region for localization.
    # - **Urgency**: How quickly the listing needs to be posted.
    # - **Tone of Voice**: Options include formal, informal, concise, or verbose.
    # - **API Key**: Required for interacting with external services.
    # - **Model Selection**: Choose the AI model to be used.
    # - **Profile Info**: Additional information such as location, etc.

    tools = [get_image_analysis]

    prompt = hub.pull("hwchase17/openai-functions-agent")

    agent_runnable = create_openai_functions_agent(llm, tools, prompt)

    tool_executor = ToolExecutor(tools)

    workflow = StateGraph(AgentState)

    execute_tools = lambda data: execute_tools_base(data, tool_executor)
    run_agent = lambda data: run_agent_base(data, agent_runnable)
    workflow.add_node("agent", run_agent)
    workflow.add_node("action", execute_tools)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent", should_continue, {"continue": "action", "end": END}
    )

    # add node to extract description json

    workflow.add_edge("action", "agent")

    app = workflow.compile()

    inputs = {
        "input": """
                You are an AI assistant that helps users to create a description for their products to sell on facebook marketplace. Your colleague has some images. You can ask him for details about the images, you decide to ask him for details about the images.

                You will need to create a description of the product in the format of a json with the following format:    {'title': 'string', 'description': 'string', 'category': 'string', 'price': 'number', 'currency': 'string', 'condition': 'string', 'location': 'string', 'brand': 'string', 'model': 'string', 'color': 'string', 'size': 'string', 'material': 'string'}    If there is any information missing, you put 'unknown', but feel free to fill in with your best guess." 
                
                Use the available tools to help you with the task.

                Also, consider if more images are needed, or whether some images should be discarded.

                At the very end, make sure to return only the three following things:
                - json description of the product. MAKE SURE IT IS IN THE CORRECT FORMAT: {'title': 'string', 'description': 'string', 'category': 'string', 'price': 'number', 'currency': 'string', 'condition': 'string', 'location': 'string', 'brand': 'string', 'model': 'string', 'color': 'string', 'size': 'string', 'material': 'string'} 
                - json images, whether each is poor, meduim, or high quality, and whether it should be discarded. There should be an entry for each image. use the image analysis tool again with a new prompt to help you with this.
                - a question for the user to answer about the product if needed
                    """
    }

    for s in app.stream(inputs):
        print("---")
        print(s)
    # Product description json
    desc_json_raw = openai_api(
        s["agent"]["agent_outcome"].dict()["return_values"]["output"],
        "extract the description json. Only return the json.",
    )

    # Image Quality json
    img_quality_json_raw = openai_api(
        s["agent"]["agent_outcome"].dict()["return_values"]["output"],
        "extract the image quality json. Only return the json.",
    )

    # Question for user
    question = openai_api(
        s["agent"]["agent_outcome"].dict()["return_values"]["output"],
        "extract the question for the user. Only return the question.",
    )

    parsers = get_parsers()
    desc_dict = parsers["final_report"].parse(desc_json_raw.content)
    img_quality_dict = parsers["image_quality"].parse(img_quality_json_raw.content)
    question.content

    title_fname = save_output(desc_dict, img_quality_dict, question, images)
    st.write(f"Product data saved to assets/model_outputs/{title_fname}")

    product_data = load_data("assets/model_outputs", title_fname)
    display_product_data(product_data)
