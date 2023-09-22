from typing import Any, Optional
import requests
from langchain.tools import BaseTool
from bs4 import BeautifulSoup
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


class RequestGetToText(BaseTool):
    name = "request_get_to_text"
    description = "Useful for when internet access to a specific page is needed, if user provides a url or after doing a search. Input should be a  url (i.e. https://www.google.com)"

    def _run(self, url: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> Any:
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()

        return text

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        return NotImplementedError("Request get to text async is not yet implemented")
