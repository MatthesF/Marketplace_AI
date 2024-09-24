from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from config import OPENAI_API_KEY, MODEL_NAME

def get_estimated_price(text_description):
    """
    Returns an estimated price based on the product description.
    """
    # Implement pricing logic here
    return '600,000 DKK'

def setup_agent():
    """
    Sets up the LangChain agent with the necessary tools and prompts.
    """
    tools = [
        Tool(
            name="get_estimated_price",
            func=get_estimated_price,
            description="Estimates the price of a product based on its description."
        )
    ]

    agent_prompt = PromptTemplate(
        template="""
You are an AI agent making second-hand product listings. You receive a text summary describing a set of images. You should output the following in Danish and English:

- Title:
- Category:
- Model number:
- Estimated price:
- Short Sales Description (EN):
- Short Sales Description (DK):

And nothing else.

Here are the image descriptions: {summary}
""",
        input_variables=["summary"]
    )

    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=0.1,
        api_key=OPENAI_API_KEY
    )

    react_prompt = hub.pull('hwchase17/react')

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=react_prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

    return agent_executor
