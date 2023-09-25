import streamlit as st

from langchain.memory import ConversationBufferMemory
from llama_customs import LlamaConversationBufferMemory

from config import LLM_MODELS


def handle_llm_change():
    model_info = LLM_MODELS[st.session_state.llm_selected]
    if LLM_MODELS[st.session_state.llm_selected].source == "openai":
        st.session_state.memory = ConversationBufferMemory(
            memory_key="memory", return_messages=True)
    elif LLM_MODELS[st.session_state.llm_selected].source == "replicate":
        st.session_state.memory = LlamaConversationBufferMemory(
            memory_key="chat_history")
    st.toast("Model Selected\n\n" + model_info.__str__(), icon="🤖")
