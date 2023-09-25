import re
import json
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate, AIMessage, HumanMessage


class AbsoluteAgent():

    def __init__(self, llm, tools: dict) -> None:
        self.llm = llm
        self.tools = tools
        self.tool_names = [k.lower() for k in tools.keys()]

    def run(self, prompt: list, callbacks=None):
        print("PROMPT: ", prompt)
        response = self.llm(prompt)
        print("RESPONSE: ", response.content)
        command_response = self._run_command(response.content)
        print("COMMAND_RESPONSE =>", command_response)
        if command_response:
            # command_prompt = prompt[-1]
            # command_prompt = {
            #     "role": "system", "content": "SERVER OUTPUT:\n" + str(command_response[1] + "\n")}
            response = self.llm(
                prompt.append(SystemMessage(content="SERVER OUTPUT:\n" + str(command_response[1]) + "\n")))
        return response

    def stream(self, prompt):
        full_response = ""
        for t in self.llm.stream(prompt):
            full_response += t
            yield t

    def _parse_for_command(self, text: str):
        lines = text.replace('```', "").split("\n")

        # Find the lines with START and END
        start_index = None
        end_index = None
        count_open_brackets = 0
        for i, line in enumerate(lines):
            if "COMMAND" in line:
                start_index = i
                break

        if start_index is None:
            return None, None

        open_count = 0
        close_count = 0
        for i, line in enumerate(lines[start_index:]):
            open_count += line.count("{")
            close_count += line.count("}")
            if open_count and open_count == close_count:
                end_index = i+start_index
                break

        # If START or END is not found, return None
        if end_index is None:
            return None, None

        command_str = "".join(
            lines[start_index:end_index+1]).replace("\n", "").strip()
        print("COMMAND_STR =>", command_str)
        return self._parse_for_command_regex(command_str)

    def _parse_for_command_regex(self, text: str):
        # pattern = r"COMMAND:\s*(?P<COMMAND>[^\s\n]+).*?(?=COMMAND_INPUT)COMMAND_INPUT:\s*(?P<COMMAND_INPUT>[^\n]+)"
        # pattern = r'COMMAND: (\w+)\s*COMMAND_INPUT: ({.*?})\s*'
        pattern = r'COMMAND: (\w+)\s*COMMAND_INPUT: (\{.*?\})'
        # match = re.search(pattern, text, re.DOTALL)
        match = re.search(pattern, text)
        if not match:
            # raise ValueError("could not parse command from text: {}".format(text))
            return None, None

        command = match.group(1).strip()
        command_input = match.group(2).strip()
        return command, command_input

    def _run_command(self, text: str):
        command = self._parse_for_command(text)
        print("COMMAND =>", command)

        if command[0] and command[0].lower() in self.tool_names:
            tool = self._get_tool_info(command[0], self.tools)
            try:
                kwargs = json.loads(command[1])
            except json.decoder.JSONDecodeError as e:
                print("\033[91m=== Failed to parse json: {}\033[0m".format(e))
            print("=> Parsing Json from this =>", command[1])
            print(type(kwargs), kwargs)
            response = tool["run"](kwargs)
            print("======SERVER======")
            print(response)
            print("======SERVER======")

            return command, str(response)

    def _get_tool_info(self, tool_name, tools_dict):
        # Normalize the tool_name to lowercase
        tool_name_lower = tool_name.lower()

        # Search for the tool in the dictionary
        for key, value in tools_dict.items():
            if key.lower() == tool_name_lower:
                return value
        return None

    def _format_message(self, message: dict):
        message_map = {
            "user": HumanMessage,
            "system": SystemMessage,
            "assistant": AIMessage,
        }
        return message_map[message["role"]](message["content"])

    def _format_messages(self, messages: list):
        return [self._format_message(m) for m in messages]


if __name__ == "__main__":
    test = """```
START
COMMAND: NewsSearch COMMAND_INPUT: { "query": "San Francisco news" }
END
```"""

    print(AbsoluteAgent(
        None, {"search": {"run": lambda x: print(x)}})._parse_for_command(test))
