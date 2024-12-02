import streamlit as st
from src.graph.state import GraphState

def initialize_session_state():
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 1
    if "processed_images" not in st.session_state:
        st.session_state.processed_images = [None] * len(st.session_state.uploaded_files)
    if "recommendation" not in st.session_state:
        st.session_state.recommendation = ""
    if "which_run" not in st.session_state:
        st.session_state.which_run = None
    if "graph_state" not in st.session_state:
        st.session_state.graph_state = GraphState()
    if "thread" not in st.session_state:
        st.session_state.thread = {"configurable": {"thread_id": "777"}}
