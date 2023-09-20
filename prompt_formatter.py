from transformers import AutoTokenizer, LlamaTokenizer
import os


class BasePromptFormatter():

    SYSTEM_START = ""
    SYSTEM_END = ""

    USER_START = ""
    USER_END = ""

    BOT_START = ""
    BOT_END = ""

    def __init__(self, model_id=""):
        self.tokenizer = None

    def token_count(self, text):
        return len(self.tokenizer.encode(text))

    def make_system_prompt(self, system):
        return self.SYSTEM_START + system + self.SYSTEM_END if system else ""

    def user_prompt(self, text):
        return self.USER_START + text + self.USER_END if text else ""

    def bot_prompt(self, text):
        return self.BOT_START + text + self.BOT_END if text else ""

    def make_history_prompt(self, history):
        return "".join(self.user_prompt(data["role"]) + self.bot_prompt(data["content"]) for data in history) if history else ""

    def max_history(self, history=[], system="", message="", max_tokens=1000) -> [(str, str)]:
        """
        TODO: make history inversed, it is checking from the origin of time to the future, when it needs to check from the current to the past. so the coutoff includes the latest,
        Make Summary of History?
        """
        max_history = []
        try:
            token_count = self.token_count(
                self.make_system_prompt(system) + self.user_prompt(message))
        except Exception as e:
            print("Error: no self.tokenizer")
            print(e)
            return history

        for data in history[::-1]:
            token_count += self.token_count(str(data[0]) + str(data[1]))
            if token_count < max_tokens:
                max_history.append(data)
            else:
                return max_history[::-1]
        return max_history[::-1]

    def make_prompt(self, message="", history=[], system="", max_tokens=1000) -> str:
        max_history = self.max_history(
            history=history, system=system, message=message, max_tokens=max_tokens)
        return self.make_system_prompt(system) + self.make_history_prompt(max_history) + self.user_prompt(message)


class LLaMaPrompt(BasePromptFormatter):
    BOS = '<s>'
    EOS = '</s>'
    CRLF = '\n'
    INSTRUCTION_START = "[INST]"
    INSTRUCTION_END = "[/INST]"

    SYSTEM_START = BOS + INSTRUCTION_START + '<<SYS>>' + CRLF
    SYSTEM_END = CRLF + "<</SYS>>" + CRLF*2

    USER_START = BOS + INSTRUCTION_START
    USER_END = INSTRUCTION_END

    BOT_START = ""
    BOT_END = EOS

    def __init__(self, model_id="TheBloke/Llama-2-7B-chat-GPTQ"):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "bert-base-uncased")
        self.tokenizer.save_pretrained("./tokenizers/llama-7b-chat-gptq")

    def make_prompt(self, message="", history=[], system="", max_tokens=2000):
        return super().make_prompt(message, history, system, max_tokens=max_tokens).replace(self.SYSTEM_END + self.USER_START, self.SYSTEM_END)


class LLaMaPromptGPTQ(BasePromptFormatter):
    BOS = ''
    EOS = ''
    CRLF = '\n'
    INSTRUCTION_START = "[INST]"
    INSTRUCTION_END = "[/INST]"

    SYSTEM_START = BOS + INSTRUCTION_START + '<<SYS>>' + CRLF
    SYSTEM_END = CRLF + "<</SYS>>" + CRLF

    USER_START = BOS + INSTRUCTION_START
    USER_END = INSTRUCTION_END + CRLF

    BOT_START = ""
    BOT_END = EOS + CRLF

    def make_prompt(self, message="", history=[], system=""):
        return super().make_prompt(message, history, system).replace(self.SYSTEM_END + self.USER_START, self.SYSTEM_END)


class SimpleLLaMaPrompt(BasePromptFormatter):
    CRLF = '\n'

    SYSTEM_START = "SYSTEM: "
    SYSTEM_END = CRLF

    USER_START = "USER: "
    USER_END = CRLF

    BOT_START = "ASSISTANT: "
    BOT_END = CRLF


if __name__ == '__main__':
    message = "how is the weather today?"
    # message = None
    history = [("hello, how are you?", "good and you?"),
               ("great, thanks for asking", "glad you are doing well")]
    # history = []
    system = "you are are a honest assistant"
    # system = None

    formatter = LLaMaPrompt()
    simpleFormatter = SimpleLLaMaPrompt()
    print(formatter.make_prompt(message, history, system, max_tokens=10))
    print("-------------")
    print(simpleFormatter.make_prompt(message, history, system))
