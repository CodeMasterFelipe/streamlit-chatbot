import streamlit as st

from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate, AIMessage, HumanMessage
from langchain.callbacks import StreamlitCallbackHandler

from agent_manager import initialize_agent_executor
from tool_manager import load_tools
from handlers import handle_llm_change
from config import LLM_MODELS


class ChatbotApp:

    def __init__(self):
        self.model_name = "GPT 3.5-turbo"
        self.model_info = LLM_MODELS[self.model_name]
        self.initialize_state()

        st.session_state["llm_selected"] = self.model_name
        handle_llm_change()

    def initialize_state(self):
        if "memory" not in st.session_state:
            st.session_state["memory"] = None
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant",
                 "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
            ]

    def create_sidebar(self):
        with st.sidebar:
            self.model_name = st.selectbox(
                "Select a model", LLM_MODELS.keys(), 0, on_change=handle_llm_change, key="llm_selected")
            self.model_info = LLM_MODELS[self.model_name]

    def handle_chat(self, prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # st.session_state.openai_messages.append(HumanMessage(content=prompt))
        st.chat_message("user").write(prompt)
        agent_executor = initialize_agent_executor(
            self.model_name, load_tools(), st.session_state.memory)
        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(
                st.container(), expand_new_thoughts=True)
            response = agent_executor.run(prompt, callbacks=[st_cb])
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
            st.write(response)

    def run(self):
        self.create_sidebar()
        st.title("Chat with Search")
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
        if prompt := st.chat_input(placeholder="Type here your message"):
            self.handle_chat(prompt)


if __name__ == "__main__":
    app = ChatbotApp()
    app.run()
