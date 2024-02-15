from bs4 import BeautifulSoup
import requests

def get_url_response(url: str, timeout: tuple = (1, 1), **kwargs) -> requests.Response:
    """
    Sends a GET request to a URL and returns the response.

    Args:
        url (str): The URL to send the GET request to.
        timeout (tuple): A tuple specifying the connection and read timeouts in seconds.
                         Defaults to (1, 1).
        **kwargs: Additional keyword arguments to be passed to the requests.get() function.

    Returns:
        requests.Response: A Response object containing the server's response to the GET request.

    Raises:
        TimeoutError: If a timeout occurs while requesting or reading the response.
        Exception: If an error other than a timeout occurs during the request.
    """
    try:
        response = requests.get(url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectTimeout:
        raise TimeoutError(f"Timeout: requesting >{timeout[0]} seconds.")
    except requests.exceptions.ReadTimeout:
        raise TimeoutError(f"Timeout: reading >{timeout[1]} seconds.")
    except Exception as e:
        raise e
    
def get_url_content(url: str) -> str:
    """
    Retrieve and parse the content from a given URL.

    Args:
        url (str): The URL to fetch and parse.

    Returns:
        str: The text content extracted from the URL.

    Raises:
        ValueError: If there is an issue during content retrieval or parsing.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        text_content = ' '.join([p.get_text() for p in soup.find_all('p')])
        return text_content
    except Exception as e:
        raise f"Error fetching content for {url}: {e}"
    