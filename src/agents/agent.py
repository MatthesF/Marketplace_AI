from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
import operator
from typing import TypedDict, Annotated, List, Union

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from src.tools import recommendation_tool
from config import OPENAI_API_KEY,MODEL_NAME   
from src.prompts import agent_prompt
from langchain.prompts import PromptTemplate

class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


# Workflow functions
def run_agent_base(data, agent_runnable):
    agent_outcome = agent_runnable.invoke(data)
    return {"agent_outcome": agent_outcome}


def execute_tools_base(data, tool_executor):
    agent_action = data["agent_outcome"]
    output = tool_executor.invoke(agent_action)
    return {"intermediate_steps": [(agent_action, str(output))]}


def should_continue(data):

    if isinstance(data["agent_outcome"], AgentFinish):
        return "end"
    else:
        return "continue"

def initialize_new_agent():
    tools = [recommendation_tool]
    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=0.1,
        stop=["\nObservation", "Observation"],
        api_key=OPENAI_API_KEY
    )
    
    prompt = PromptTemplate.from_template(template=agent_prompt).partial(
        tools=tools,
        tool_names=", ".join([t.name for t in tools]),
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True,
    ) 
    
    return agent, prompt