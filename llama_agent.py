import re
from typing import Union
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import load_tools

# memory = ConversationBufferWindowMemory(
#     memory_key="chat_history", k=5, return_messages=True, output_key="output"
# )
# tools = load_tools(["llm-math"], llm=llm)

from langchain.agents import AgentOutputParser
from langchain.agents.conversational_chat.prompt import FORMAT_INSTRUCTIONS
from langchain.output_parsers.json import parse_json_markdown
from langchain.schema import AgentAction, AgentFinish


class OutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> AgentAction | AgentFinish:
        try:
            # this will work IF the text is a valid JSON with action and action_input
            json_text = re.search(r'{.*?}', text, re.DOTALL).group(0)
            response = parse_json_markdown(json_text)
            action, action_input = response["action"], response["action_input"]
            if action == "Final Answer":
                # this means the agent is finished so we call AgentFinish
                return AgentFinish({"output": action_input}, text)
            else:
                # otherwise the agent wants to use an action, so we call AgentAction
                return AgentAction(action, action_input, text)
        except Exception:
            # sometimes the agent will return a string that is not a valid JSON
            # often this happens when the agent is finished
            # so we just return the text as the output
            return AgentFinish({"output": text}, text)

    @property
    def _type(self) -> str:
        return "conversational_chat"
