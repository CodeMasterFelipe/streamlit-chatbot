import streamlit as st

from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate, AIMessage, HumanMessage
from langchain.callbacks import StreamlitCallbackHandler

from agent_manager import initialize_agent_executor
from tool_manager import load_tools
from handlers import handle_llm_change, handle_chat_session_change, handle_new_chat_session, handle_session_deletion
from config import LLM_MODELS
from database import Database
from utils import load_css


st.set_page_config(
    page_title="Chat App",
    page_icon="🤖",
    # layout="wide",
    layout="centered",
    initial_sidebar_state="expanded",
)

# load_css("./static/css/button.css")
load_css("./static/css/chat-app.css")


class ChatbotApp:

    def __init__(self):
        self.model_name = "GPT 3.5-turbo"
        self.model_info = LLM_MODELS[self.model_name]
        self.initialize_state()

        st.session_state["llm_selected"] = self.model_name
        # handle_llm_change()

    def initialize_state(self):
        if "memory" not in st.session_state:
            st.session_state["memory"] = None
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant",
                 "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
            ]
        if "current_session" not in st.session_state:
            st.session_state["current_session"] = None
        if "db" not in st.session_state:
            st.session_state["db"] = Database()

    def create_sidebar(self):
        with st.sidebar:
            self.model_name = st.selectbox(
                "Select a model", LLM_MODELS.keys(), 0, on_change=handle_llm_change, key="llm_selected")
            self.model_info = LLM_MODELS[self.model_name]

            # Display buttons for each session
            st.subheader("Select a Chat Session")
            st.button("+ New Chat", use_container_width=True,
                      on_click=handle_new_chat_session, type="primary")

            for session in st.session_state.db.get_all_sessions():

                with st.container():
                    selected = st.session_state.current_session == session

                    if selected:
                        col1, col2 = st.columns([.85, .15], gap="small")
                        col1.button(
                            session, key=f"button_{session}", use_container_width=True, type="primary")
                        with col2:
                            st.button(
                                "🗑️", key=f"delete_{session}", on_click=lambda session_id=session: handle_session_deletion(session_id), use_container_width=True)
                            # st.button(
                            #     "✎", key=f"edit_{session}", use_container_width=True)

                    else:
                        st.button(session, key=f"button_{session}", on_click=lambda session_id=session: handle_chat_session_change(
                            session_id), use_container_width=True, type="secondary")
                    # col1, col2 = st.columns([6, 2])
                    # with col1:
                    # button = bt_container.button(
                    #     session, key=f"button_{session}", on_click=lambda session_id=session: handle_chat_session_change(session_id), use_container_width=not st.session_state.current_session == session, type=type)
                    # with col2:
                    # delete_button = bt_container.button(
                    #     "delete", key=f"delete_{session}")
                # if st.button(session):
                #     self.current_session = session
                #     st.session_state["messages"] = self.db.get_all_chats(
                #         self.current_session)

    def check_if_new_session(self):
        if "user" not in [m["role"] for m in st.session_state.messages]:
            session = st.session_state.db.create_session()
            st.session_state.current_session = session

    def handle_chat(self, prompt):
        print("Current session =>",
              st.session_state.current_session)
        self.check_if_new_session()
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.db.insert_chat(
            st.session_state.current_session, {"role": "user", "content": prompt})
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
            st.session_state.db.insert_chat(st.session_state.current_session, {
                "role": "assistant",
                "content": response
            })
            st.write(response)

    def handle_text_area_size(self):
        return st.session_state.prompt.count("\n") * 50 if "prompt" in st.session_state else 100

    def run(self):
        self.create_sidebar()
        with st.container():
            st.title("Chat with Search")
            for msg in st.session_state.messages:
                print(st.session_state.messages)
                st.chat_message(msg["role"]).write(msg["content"])

        chat_input_container = st.container()

        # with st.container():
        # prompt = st.chat_input(placeholder="Type your message here...")
        chat_input_container.button("Regenerate")
        # prompt = chat_input_container.text_input(
        #     "", placeholder="Type your message here...")
        prompt = chat_input_container.text_area(
            "", placeholder="Type your message here...", key="prompt", height=300)

        if chat_input_container.button("send"):
            self.handle_chat(prompt)


if __name__ == "__main__":
    # if "memory" not in st.session_state:
    app = ChatbotApp()
    app.run()
