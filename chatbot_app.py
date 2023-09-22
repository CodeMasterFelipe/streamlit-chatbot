from dataclasses import dataclass
import streamlit as st

from langchain.agents import initialize_agent, AgentType, AgentExecutor, load_tools, ConversationalAgent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.llms import Replicate
from langchain.tools import DuckDuckGoSearchResults

import os
from llama_customs import LlamaConversationBufferMemory, toolset_string, tool_names, system_prompt
from prompt_formatter import LLaMaPrompt
from agents.llama2_agent.base import LlamaConversationalAgent

from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory, ChatMessageHistory
from langchain.agents import load_tools

from tools.requests import RequestGetToText

prompt_formatter = LLaMaPrompt()
# replicate_token = getpass()
# os.environ["REPLICATE_API_TOKEN"] = ""

AI_NAME = "Nova"


@dataclass
class LlmModelInfo():
    source: str = "replicate"
    model: str = ""

    def __str__(self):
        return "source: {source}\n\nmodel: {model}".format(source=self.source, model=self.model.split(":")[0])

    def __dict__(self):
        return {
            "source": self.source,
            "model": self.model
        }


llm_model = {
    "LLaMa 2 7B chat": LlmModelInfo(source="replicate", model="meta/llama-2-7b-chat:8e6975e5ed6174911a6ff3d60540dfd4844201974602551e10e9e87ab143d81e"),
    "LLaMa 2 13B chat": LlmModelInfo(source="replicate", model="meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d"),
    "LLaMa 2 70B chat": LlmModelInfo(source="replicate", model="meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3"),
    "GPT 3.5-turbo": LlmModelInfo(source="openai", model="gpt-3.5-turbo-0613"),
    "GPT 4": LlmModelInfo(source="openai", model="gpt-4"),
}

if "memory" not in st.session_state:
    st.session_state["memory"] = LlamaConversationBufferMemory(
        memory_key="chat_history")

# tools = [DuckDuckGoSearchResults(
#     name="Search"), RequestGetToText(name="RequestGet")]
tools = [DuckDuckGoSearchResults(
    name="Search")]


def handle_llm_change():
    model_info = llm_model[st.session_state.llm_selected]
    if llm_model[st.session_state.llm_selected].source == "openai":
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True)
    elif llm_model[st.session_state.llm_selected].source == "replicate":
        st.session_state.memory = LlamaConversationBufferMemory(
            memory_key="chat_history")
    st.toast("Model Selected\n\n" + model_info.__str__(), icon="🤖")


with st.sidebar:
    model_name = st.selectbox(
        'Select a model', llm_model.keys(), 0, on_change=handle_llm_change, key="llm_selected")
    model_info = llm_model[model_name]

    # TODO: change type of memory to ConversationBufferWindowMemory if OpenAI
    # st.write(model_info)

st.title("Chat with search")


if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant",
            "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
    ]


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Type here your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # if not openai_api_key:
    #     st.info("Please add your OpenAI API key to continue.")
    #     st.stop()

    # llm = ChatOpenAI(model_name="gpt-3.5-turbo",
    #                  openai_api_key=openai_api_key, streaming=True)

    model_info = llm_model[model_name]

    if model_info.source == "replicate":
        llm = Replicate(
            model=model_info.model,
            streaming=True,
            model_kwargs=dict(
                temperature=0.7,
                # max_length=2000,
                max_new_tokens=2000,
                top_p=0.95,
                system_prompt=system_prompt.format(
                    ai_name=AI_NAME, toolset=toolset_string(tools), tool_names=tool_names(tools)),
            ),
        )
        agent = LlamaConversationalAgent.from_llm_and_tools(
            llm=llm, tools=tools, ai_prefix=AI_NAME)
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, memory=st.session_state.memory
        )
    elif model_info.source == "openai":
        llm = ChatOpenAI(
            model_name=model_info.model,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            streaming=True,
        )
        # agent = ConversationalAgent.from_llm_and_tools(
        #     llm=llm, tools=tools, ai_prefix=AI_NAME)
        agent_executor = initialize_agent(
            tools,
            llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            # agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            # max_iterations=5,
            # early_stopping_method="generate",
            # memory=st.session_state.memory,
        )

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(
            st.container(), expand_new_thoughts=True)
        if model_info.source == "openai":
            response = agent_executor.run(
                prompt, callbacks=[st_cb])
        elif model_info.source == "replicate":
            response = agent_executor.run(prompt, callbacks=[st_cb])

        st.session_state.messages.append(
            {"role": "assistant", "content": response})
        # print(st.session_state.messages)
        # print(st.session_state.memory.chat_memory.messages)
        st.write(response)
