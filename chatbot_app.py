import streamlit as st

from langchain.agents import initialize_agent, AgentType
from langchain.agents import load_tools
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.llms import Replicate
from langchain.tools import DuckDuckGoSearchRun

import os
from getpass import getpass
from llama_agent import OutputParser
from prompt_formatter import LLaMaPrompt

from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import load_tools

prompt_formatter = LLaMaPrompt()
# replicate_token = getpass()
# os.environ["REPLICATE_API_TOKEN"] = ""


def get_system_prompt(tools):
    tool_names_str = ", ".join([tool.name for tool in tools])
    return """Assistant is a expert JSON builder designed to assist with a wide range of tasks.

Assistant is able to respond to the User and use tools using JSON strings that contain "action" and "action_input" parameters. If you want to communicate with the user do so with the action = "Final Answer" and action_input = "what you want to say".

All of Assistant's communication is performed using this JSON format.

Assistant can also use tools by responding to the user with tool use instructions in the same "action" and "action_input" JSON format. Tools available to Assistant are:

- "Search": Useful for when you need to answer questions that requires the internet to be able to answer the question.:
    ```json
    {{"action": "Search",
      "action_input": "search query"}}
    ```

Here are some previous conversations between the Assistant and User:

User: Hey how are you today?
Assistant: ```json
{{"action": "Final Answer",
 "action_input": "I'm good thanks, how are you?"}}
```
User: I'm great, what is the weather today in Seattle?
Assistant: ```json
{{"action": "Search",
 "action_input": "weather Seattle"}}
```
User: 72 degrees Fahrenheit
Assistant: ```json
{{"action": "Final Answer",
 "action_input": "It looks like the answer is 72 degrees!"}}
```

Here is the latest conversation between Assistant and User.
"""


with st.sidebar:
    openai_api_key = st.text_input(
        "OpenAI API Key", key="langchain_search_api_key_openai", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/pages/2_Chat_with_search.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("🔎 LangChain - Chat with search")

"""
In this example, we're using `StreamlitCallbackHandler` to display the thoughts and actions of an agent in an interactive Streamlit app.
Try more LangChain 🤝 Streamlit Agent examples at [github.com/langchain-ai/streamlit-agent](https://github.com/langchain-ai/streamlit-agent).
"""

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    # [
    #     {"role": "assistant",
    #         "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
    # ]


# for msg in st.session_state.messages:
#     st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Who won the Women's U.S. Open in 2018?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # if not openai_api_key:
    #     st.info("Please add your OpenAI API key to continue.")
    #     st.stop()
    search = DuckDuckGoSearchRun(name="Search")

    # llm = ChatOpenAI(model_name="gpt-3.5-turbo",
    #                  openai_api_key=openai_api_key, streaming=True)
    llm = Replicate(
        model="meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d",
        streaming=True,
        model_kwargs=dict(
            temperature=0.01,
            max_length=2000,
            top_p=0.95,
            # system_prompt=get_system_prompt([search])
        ),
    )
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", k=5, return_messages=True, output_key="output")
    # tools = load_tools(["llm-math"], llm=llm)

    # tools = [search]
    tools = []
    parser = OutputParser(tools=tools)
    agent = initialize_agent(
        tools, llm,
        # agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        agent="chat-conversational-react-description",
        handle_parsing_errors=True,
        # verbose=True,
        agent_kwargs={"output_parser": parser},
        # stop=["\nObservation"]
        early_stopping_method="generate",
        memory=memory,
    )

    new_prompt = agent.agent.create_prompt(
        system_message=get_system_prompt([search]),
        tools=tools
    )
    agent.agent.llm_chain.prompt = new_prompt
    instruction = "[INST]" + \
        " Respond to the following in JSON with 'action' and 'action_input' values " + \
        "[/INST]"
    human_msg = instruction + "\nUser: {input}"

    agent.agent.llm_chain.prompt.messages[2].prompt.template = human_msg

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(
            st.container(), expand_new_thoughts=False)

        print(st.session_state.messages)

        # response = agent.run(st.session_state.messages, callbacks=[st_cb])
        response = agent.run(prompt, callbacks=[st_cb])

        st.session_state.messages.append(prompt_formatter.bot_prompt(response))
        # {"role": "assistant", "content": response})
        st.write(response)
