import asyncio
from typing import Any, Type, Callable, Mapping
import logging
import aiohttp
from aiocache import cached
from functools import lru_cache
import re
import httpx
from bs4 import BeautifulSoup


@lru_cache(maxsize=None)
def api_endpoint_from_url(request_url: str) -> str:
    match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
    return match[2] if match else ""


async def get_url_response(
    url: str, timeout: tuple = (1, 1), **kwargs
) -> httpx.Response:
    """
    Sends a GET request to a URL and returns the response.

    Args:
        url (str): The URL to send the GET request to.
        timeout (tuple): A tuple specifying the connection and read timeouts in seconds.
                         Defaults to (1, 1).
        **kwargs: Additional keyword arguments to be passed to the httpx.get() function.

    Returns:
        httpx.Response: A Response object containing the server's response to the GET request.

    Raises:
        TimeoutError: If a timeout occurs while requesting or reading the response.
        Exception: If an error other than a timeout occurs during the request.
    """
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout[0], read=timeout[1])
        ) as client:
            response = await client.get(url, **kwargs)
            response.raise_for_status()
            return response
    except httpx.ConnectTimeout:
        raise TimeoutError(f"Timeout: requesting >{timeout[0]} seconds.")
    except httpx.ReadTimeout:
        raise TimeoutError(f"Timeout: reading >{timeout[1]} seconds.")
    except Exception as e:
        raise e


async def get_url_content(url: str, timeout=(2, 2), **kwargs) -> str:
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
        response = await get_url_response(url=url, timeout=timeout, **kwargs)
        soup = BeautifulSoup(response.text, "html.parser")

        text_content = " ".join([p.get_text() for p in soup.find_all("p")])
        return text_content
    except Exception as e:
        raise ValueError(f"Error fetching content for {url}: {e}")
