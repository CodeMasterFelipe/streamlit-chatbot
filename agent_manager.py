import os

from langchain.agents import initialize_agent, AgentType
from langchain.llms import Replicate
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import MessagesPlaceholder, SystemMessage

from agents.absolute_agent.base import AbsoluteAgent
from config import LLM_MODELS


def initialize_agent_executor(model_name, tools, memory, agent_kwargs=None):
    model_info = LLM_MODELS[model_name]

    if agent_kwargs is None:
        agent_kwargs = {
            "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
            "system_message": SystemMessage(content="Your Name is Nova, and you are a very helpful AI assistant that has tools at her disposal."),
        }

    if model_info.source == "replicate":
        # Your existing code to initialize agent_executor for replicate source
        llm = Replicate(
            model=model_info.model,
            streaming=True,
            model_kwargs=dict(
                temperature=0.7,
                # max_length=2000,
                max_new_tokens=2000,
                top_p=0.95,
                # system_prompt=system_prompt.format(
                #     tools_formatted=format_tools_prompt(tools)),
                # system_prompt=system_prompt.format(
                #     ai_name=AI_NAME, toolset=toolset_string(tools), tool_names=tool_names(tools)),
            ),
        )
        agent_executor = AbsoluteAgent(llm, tools)
    elif model_info.source == "openai":
        # Your existing code to initialize agent_executor for openai source
        llm = ChatOpenAI(
            model_name=model_info.model,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            streaming=True,
        )
        agent_executor = initialize_agent(
            tools,
            llm,
            # agent=AgentType.OPENAI_FUNCTIONS,
            agent=AgentType.OPENAI_MULTI_FUNCTIONS,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            # streaming=True,
            memory=memory,
            agent_kwargs=agent_kwargs,
        )

    return agent_executor
