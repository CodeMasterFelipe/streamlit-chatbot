import requests
from bs4 import BeautifulSoup


def read_web_page(url):
    """
    Read a web page and return its content.
    this returns just the text, there is no urls in the return content.

    Parameters
    ----------
    url : str
        The URL of the web page to read.

    Returns
    -------
    str
        The content of the web page.
    """
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for any HTTP errors

        # Obtain the HTML content of the web page
        html_content = response.text

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # # Extract the desired information from the web page
        # paragraphs = soup.find_all("p")

        # # Process and return the extracted data
        # extracted_text = [p.text for p in paragraphs]
        # return extracted_text
        return soup.get_text()

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving web page: {e}")


if __name__ == "__main__":
    # Example usage

    print(read_web_page("https://python.langchain.com/docs/get_started/introduction"))
