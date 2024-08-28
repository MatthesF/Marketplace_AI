from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import torch
import streamlit as st
import base64
import requests
from io import BytesIO
import os


import dotenv
dotenv.load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain.tools import Tool




def get_image_desc(image):

    # Template for summary prompt
    summary_template = """
    Descriabe the folowing image:
    {image}
    """

    # Create the prompt template
    summary_prompt_template = PromptTemplate(input_variables=["image"], template=summary_template)

    # Create the LLM instance
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0, 
        api_key=openai_api_key
    )

    # Combine the template and LLM into a chain
    chain = LLMChain(prompt=summary_prompt_template, llm=llm)

    # Run the chain with the provided information
    res = chain.run(image=image)

    return res

def encode_image(image_file):
    """
    Encodes the image to base64
    """
    #with open(image_path, "rb") as image_file:
    buffered = BytesIO()
    image_file.save(buffered,format="png")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def encode_images(image_list):
    return [encode_image(image) for image in image_list]

def make_image_small(image_path, size=(512, 512)):
    """
    Makes the image small, and saves it
    """
    from PIL import Image
    im = Image.open(image_path)
    im = im.resize(size)
    ext = os.path.splitext(image_path)[1]
    im.save(image_path.replace(ext, f'_small{ext}'))

def obtain_small_name(image_path):
    """
    Returns the name of the small image, from the original image path
    """
    ext = os.path.splitext(image_path)[1]
    return image_path.replace(ext, f'_small{ext}')

def get_image_description(image_files):
	"""
	Gets the description of the images, from the image path
	"""
	# Making the image small
	#make_image_small(image_path)
	#image_path = obtain_small_name(image_path)


	# Getting the base64 string
	base64_images = encode_images(image_files)

	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {openai_api_key}"
	}

	payload = {
		"model": "gpt-4o-mini",
		"messages": [
			{
			"role": "user",
			"content": [
				{
				"type": "text",
				"text": "What’s in this image? You should focus on the object and its condition. If you recognize the brand name, please state it."
				},
				
			]
			}	
	],
	"max_tokens": 300
	}
    

	for image in base64_images:
		payload["messages"][0]["content"] += [{
				"type": "image_url",
				"image_url": {
					"url": f"data:image/jpeg;base64,{image}"
				}
				}]
     

	response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

	return response.json()

st.title("Project")

# make image to vector with CLIP
uploaded_file = st.file_uploader(
    "Choose a Image file", accept_multiple_files=True, type="png"
)

with st.sidebar:
     offline = st.radio('offline', [True, False])


cols = st.columns(2)

if uploaded_file is not None:
    with cols[0]:
        images = []
        for file in uploaded_file:
            image = Image.open(file)
            images.append(image)
            st.image(image)

    with cols[1]:
        if not offline:
            desc = get_image_description(images)
            np.savez('desc.npz', desc)
        else:
             desc = np.load('desc.npz', allow_pickle=1)
             desc = desc[desc.files[0]]
             st.write(desc)
        #st.write(desc["choices"][0]["message"]["content"])


######### AGENT
# Recieves 


def get_estimated_price(text_description):
     """
     Function gets description of product, and returns estimated price
     """
     return '600000 dkk'

tools = [
Tool(name = get_estimated_price.__name__,func=get_estimated_price,description=get_estimated_price.__doc__)
     
]

agent_prompt = """
You are an AI agent making second hand product listings. You revice a text summary describing a set of images. You should output the folowing in Danish and English:

Title:
Category:
Model nr:
Estimated price:
Short Sales Description (en):
Short Sales Description (dk):

And nothing else.

Here are the image descriptions: {summary}
"""

prompt = PromptTemplate.from_template(template=agent_prompt).partial(
    tools=tools,
    tool_names=", ".join([t.name for t in tools]),
)

llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.1, stop= ["\nObservation", "Observation"],api_key=openai_api_key)


react_prompt = hub.pull('hwchase17/react')

agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)


agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

response = agent_executor.invoke(input={'input': prompt.format(summary=desc)})
print(response)
st.write(response)

