import streamlit as st

from langchain.memory import ConversationBufferMemory
from llama_customs import LlamaConversationBufferMemory

from config import LLM_MODELS

MEMORY_MAP = {
    "openai": ConversationBufferMemory,
    "replicate": LlamaConversationBufferMemory
}


def handle_llm_change():
    model_info = LLM_MODELS[st.session_state.llm_selected]
    if LLM_MODELS[st.session_state.llm_selected].source == "openai":
        st.session_state.memory = ConversationBufferMemory(
            memory_key="memory", return_messages=True)
    elif LLM_MODELS[st.session_state.llm_selected].source == "replicate":
        st.session_state.memory = LlamaConversationBufferMemory(
            memory_key="chat_history")
    st.toast("Model Selected\n\n" + model_info.__str__(), icon="🤖")


def handle_chat_session_change(session_id):
    # session_id = st.session_state.chat_session_id_selected
    st.session_state.current_session = session_id
    all_chats = st.session_state.db.get_all_chats(session_id)
    print("Loaded Session Chats =>", all_chats)
    st.session_state.messages = all_chats


def handle_new_chat_session():
    st.session_state.current_session = None
    st.session_state.messages = []
    st.session_state.memory = MEMORY_MAP[LLM_MODELS[st.session_state.llm_selected].source](
        memory_key="memory", return_messages=True)


def handle_session_deletion(session_id):
    st.session_state.db.delete_session(session_id)
