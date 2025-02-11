import streamlit as st
from streamlit_chat import message

from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate, AIMessage, HumanMessage
from langchain.callbacks import StreamlitCallbackHandler

from agent_manager import initialize_agent_executor
from tool_manager import load_tools
from handlers import handle_llm_change, handle_chat_session_change, handle_new_chat_session, handle_session_deletion
from config import LLM_MODELS
from db.database import Database
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
st.write(
    """<style>
    [data-testid="stHorizontalBlock"]:has(.stSelectbox) {
        align-items: end;
        justify-content: flex-start;
        
    }
    [data-testid="stHorizontalBlock"] .stSelectbox {
        background-color: transparent;
    }
    [data-testid="stHorizontalBlock"] .stSelectbox [data-baseweb="select"] div {
        background-color: transparent;
        font-size: 1.3em;
        font-weight: bold;
        border: none;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)


class ChatbotApp:

    def __init__(self):
        self.model_name = "GPT 3.5-turbo"
        self.model_info = LLM_MODELS[self.model_name]
        self.initialize_state()

        # st.session_state["llm_selected"] = self.model_name
        # handle_llm_change()

    def initialize_state(self):
        if "llm_selected" not in st.session_state:
            st.session_state["llm_selected"] = "GPT 3.5-turbo"
        if "memory" not in st.session_state:
            st.session_state["memory"] = None
            handle_llm_change()
        if "messages" not in st.session_state:
            st.session_state["messages"] = []
        if "current_session" not in st.session_state:
            st.session_state["current_session"] = None
        if "db" not in st.session_state:
            st.session_state["db"] = Database()

    def handle_change_session_name(self, session_id):
        st.session_state.db.set_session_name(
            session_id, st.session_state.new_session_name)

    def session_popup(self, session_id, popup_container):
        with popup_container:
            st.markdown("<div id='popup-modal'></div>", unsafe_allow_html=True)
            st.button("")
            with st.container():
                st.markdown("<h3 id='session-popup'>Session Popup</h3>",
                            unsafe_allow_html=True)
                text_input = st.text_input(
                    "Session Name:", key="new_session_name")

                if text_input:
                    print("change session name => ", text_input)
                    self.handle_change_session_name(session_id)

                with st.container():
                    st.button("Confirm", on_click=lambda: self.handle_change_session_name(
                        session_id))
                    st.button("Cancel")

    def create_sidebar(self):
        with st.sidebar:
            self.model_name = st.selectbox(
                "Select a model", LLM_MODELS.keys(), 0, on_change=handle_llm_change, key="llm_selected")
            self.model_info = LLM_MODELS[self.model_name]

            # Display buttons for each session

            popup_container = st.container()
            # popup_container.write("hello world")

            with st.container():
                st.markdown("<h3 id='session-header'>Select a Chat Session</h3>",
                            unsafe_allow_html=True)
                # st.subheader(
                #     "<span id='chat-session-header'>Select a Chat Session</span>")
                st.button("\u002B New Chat", use_container_width=True,
                          on_click=handle_new_chat_session, type="secondary")
                for session in st.session_state.db.get_all_sessions():
                    # print(session)
                    session_id = session["session_id"]
                    session_name = session["session_name"]
                    st.session_state["is_popup_open"] = False
                    with st.container():
                        selected = st.session_state.current_session == session_id

                        if selected:
                            # col1, col2, col3 = st.columns(
                            #     [.8, .1, .1], gap="small")
                            st.button(
                                session_name, key=f"button_{session_id}", use_container_width=True, type="primary")
                            with st.container():
                                st.button(
                                    "X", key=f"delete_{session_id}", on_click=lambda session_id=session_id: handle_session_deletion(session_id), use_container_width=True)
                                edit = st.button(
                                    "✎", key=f"edit_{session_id}", use_container_width=True, on_click=lambda session_id=session_id: self.session_popup(session_id, popup_container))
                                # if edit:
                                #     print("hello")
                                #     with popup_container:
                                #         st.write("whatup?")
                                #         s_name = st.text_input("session name")
                                #         st.button("Confirm")

                        else:
                            st.button(session_name, key=f"button_{session_id}", on_click=lambda session_id=session_id: handle_chat_session_change(
                                session_id), use_container_width=True, type="secondary")
            # for session in st.session_state.db.get_all_sessions():

            #     with st.container():
            #         selected = st.session_state.current_session == session

            #         if selected:
            #             col1, col2, col3 = st.columns(
            #                 [.8, .1, .1], gap="small")
            #             col1.button(
            #                 session, key=f"button_{session}", use_container_width=True, type="primary")
            #             with col2:
            #                 st.button(
            #                     "X", key=f"delete_{session}", on_click=lambda session_id=session: handle_session_deletion(session_id), use_container_width=True)
            #             with col3:
            #                 st.button(
            #                     "✎", key=f"edit_{session}", use_container_width=True)

            #         else:
            #             st.button(session, key=f"button_{session}", on_click=lambda session_id=session: handle_chat_session_change(
            #                 session_id), use_container_width=True, type="secondary")

    def check_if_new_session(self):
        if "user" not in [m["role"] for m in st.session_state.messages]:
            session = st.session_state.db.create_session()
            st.session_state.current_session = session

    def handle_chat(self, prompt):
        # print("Current session =>",
        #       st.session_state.current_session)
        self.check_if_new_session()
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.db.insert_chat(
            st.session_state.current_session, {"role": "user", "content": prompt})
        # st.session_state.openai_messages.append(HumanMessage(content=prompt))
        st.chat_message(
            "user", avatar="./static/assets/user-avatar.png").write(prompt)

        character_info = st.session_state.db.get_character(
            st.session_state.character)
        agent_executor = initialize_agent_executor(
            st.session_state.llm_selected, load_tools(), st.session_state.memory, character_info)
        with st.chat_message("assistant", avatar="./db/images/Assistant.png"):
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
            _, col, _ = st.columns([0.15, .7, .15])
            # col1.title("Chat with", anchor="top")
            col.selectbox(
                "Character Selection",
                st.session_state.db.get_all_characters(),
                key="character",
                label_visibility="collapsed",
                format_func=lambda x: f"Chat with {x}",
            )
        for msg in st.session_state.messages:
            # print(st.session_state.messages)
            st.chat_message(msg["role"], avatar="./db/images/Assistant.png" if msg["role"]
                            == "assistant" else "./static/assets/user-avatar.png").write(msg["content"])
            # message(msg["content"], is_user=msg["role"] ==
            #         "user", logo="https://gravatar.com/avatar/1f82b0492a0a938288c2d5b70534a1fb?s=400&d=robohash&r=x")

        chat_input_container = st.container()

        # message("A message")
        # message("Another message", is_user=True)

        # with st.container():
        chat_input_container.button("Regenerate")
        prompt = chat_input_container.chat_input(
            placeholder="Type your message here...")
        # prompt = chat_input_container.text_input(
        #     "", placeholder="Type your message here...")
        # prompt = chat_input_container.text_area(
        #     "", placeholder="Type your message here...", key="prompt")

        if prompt:
            self.handle_chat(prompt)

        # if chat_input_container.button("send"):
        #     self.handle_chat(prompt)


if __name__ == "__main__":
    # if "memory" not in st.session_state:
    app = ChatbotApp()
    app.run()
