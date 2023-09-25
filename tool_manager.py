from langchain.tools import Tool, StructuredTool
from tools.websearch import web_search, news_search
from tools.file_operations import create_file, write_to_file, read_file_content
from tools.webscraping import read_web_page


def load_tools():
    return [
        Tool(
            name="Search",
            func=web_search,
            description="Search the web for a specific topic. This is the most general search, and its preferred to use the other search tools if possible."
        ),
        Tool(
            name="NewsSearch",
            func=news_search,
            description="Search the web for news related queries."
        ),
        Tool(
            name="WebScraping",
            func=read_web_page,
            description="Given an Url will get the content of the page."
        ),
        StructuredTool.from_function(
            name="WriteFile",
            func=write_to_file,
            description="write content to file. format = {'filename': 'file name.extension', 'content': 'content to write to file'}",
        ),
        StructuredTool.from_function(
            name="ReadFile",
            func=read_file_content,
            description="read the content of a file."
        ),
        Tool(
            name="CreateFile",
            func=create_file,
            description="create file"
        ),
    ]
