from models import LlmModelInfo

LLM_MODELS = {
    "GPT 3.5-turbo": LlmModelInfo(source="openai", model="gpt-3.5-turbo-0613"),
    "GPT 3.5 16k": LlmModelInfo(source="openai", model="gpt-3.5-turbo-16k-0613"),
    "GPT 4": LlmModelInfo(source="openai", model="gpt-4-0613"),
    "LLaMa 2 7B chat": LlmModelInfo(source="replicate", model="meta/llama-2-7b-chat:8e6975e5ed6174911a6ff3d60540dfd4844201974602551e10e9e87ab143d81e"),
    "LLaMa 2 13B chat": LlmModelInfo(source="replicate", model="meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d"),
    "LLaMa 2 70B chat": LlmModelInfo(source="replicate", model="meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3"),
    # "GPT 3.5-turbo": LlmModelInfo(source="openai", model="gpt-3.5-turbo"),
}
