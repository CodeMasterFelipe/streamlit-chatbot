# from tools.websearch import web_search, places_search, news_search

# - Weather: Get the weather for a specific city.
#   JSON Format: `{"query": "city"}`


def format_tool(tool_name: str, tool_info: dict()):
    return f"- {tool_name}: {tool_info['description']}\n  JSON Format: {tool_info['format']}\n"


def format_tools_prompt(tools: dict(dict())):
    return "\n".join([format_tool(tool_name, tool_info) for tool_name, tool_info in tools.items()])


# if __name__ == '__main__':
#     test = {
#         "Search": {
#             "description": "Search the web for a specific topic.",
#             "run": web_search,
#             "format": '{"query": "specific topic or question"}'
#         },
#         "PlacesSearch": {
#             "description": "Search the web for a specific topic.",
#             "run": places_search,
#             "format": '{"query": "specific topic or question"}'
#         },
#         "NewsSearch": {
#             "description": "Search the web for a specific topic.",
#             "run": news_search,
#             "format": '{"query": "specific topic or question"}'
#         },
#     }
#     print(format_tools_prompt(test))
