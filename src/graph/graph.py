from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import List, TypedDict
from src.graph.state import GraphState
from src.graph.nodes import *
import streamlit as st


# Load environment variables
load_dotenv()



def rag(state: GraphState) -> None:
    print("---RAG Step---")

def item_description_gen(state: GraphState) -> None:
    print("---Item Description Generation Step---")

def item_description_confirm(state: GraphState) -> None:
    print("---Item Description Confirmation Step---")

def item_post(state: GraphState) -> None:
    print("---Item Post Step---")

def user_input():
    pass

def state_user_next_step(state: GraphState) -> str:
    return state["user_next_step"]

# Build the state graph
builder = StateGraph(GraphState)

# Add nodes (ensure no duplicate keys)
builder.add_node("image_choice", image_choice)
builder.add_node("user_chosen_next_step", user_chosen_next_step)
builder.add_node("rag", rag)
builder.add_node("item_description_gen", item_description_gen)
builder.add_node("item_description_confirm", item_description_confirm)
builder.add_node("item_post", item_post)

# Define edges
builder.add_edge(START, "image_choice")
builder.add_edge("image_choice", "user_chosen_next_step")

# Add conditional edges for image recommendation
builder.add_conditional_edges(
    "user_chosen_next_step",
    state_user_next_step,
    {
        "regenerate": "image_choice",
        "sufficient": "rag",
    },
)

builder.add_edge("rag", "item_description_gen")
builder.add_edge("item_description_gen", "item_description_confirm")

# Add conditional edges for item description confirmation
builder.add_conditional_edges(
    "item_description_confirm",
    user_input,
    {
        "user_update": "item_description_gen",
        "sufficient": "item_post",
    },
)

builder.add_edge("item_post", END)

# Set up memory
memory = MemorySaver()

# Compile the graph
graph = builder.compile(
    checkpointer=memory, 
    interrupt_before=["user_chosen_next_step", "item_description_confirm"]
)

# Generate and save graph visualization
if __name__ == "__main__":
    graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
