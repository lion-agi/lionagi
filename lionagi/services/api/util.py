from __future__ import annotations

import asyncio
from collections.abc import Mapping, Callable, Coroutine
from functools import lru_cache
from typing import Any
import logging
import aiocache
import aiohttp


def api_method(http_session: aiohttp.ClientSession, method: str = "post") -> Callable:
    """
    Returns the corresponding HTTP method function from the http_session object.

    Args:
            http_session: The session object from the aiohttp library.
            method: The HTTP method as a string.

    Returns:
            The Callable for the specified HTTP method.

    Raises:
            ValueError: If the method is not one of the allowed ones.

    Examples:
            >>> session = aiohttp.ClientSession()
            >>> post_method = APIUtil.api_method(session, "post")
            >>> print(post_method)
            <bound method ClientSession._request of <aiohttp.client.ClientSession object at 0x...>>
    """
    if method in {"post", "delete", "head", "options", "patch"}:
        return getattr(http_session, method)
    else:
        raise ValueError(
            "Invalid request, method must be in ['post', 'delete', 'head', 'options', 'patch']"
        )


@lru_cache(maxsize=None)
def api_endpoint_from_url(request_url: str) -> str:
    import re

    match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
    return match[2] if match else ""


async def get_url_response(url: str, timeout: tuple = (1, 1), **kwargs):
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
    import httpx

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
    from bs4 import BeautifulSoup

    try:
        response = await get_url_response(url=url, timeout=timeout, **kwargs)
        soup = BeautifulSoup(response.text, "html.parser")

        text_content = " ".join([p.get_text() for p in soup.find_all("p")])
        return text_content
    except Exception as e:
        raise ValueError(f"Error fetching content for {url}: {e}")


class AsyncUtil:

    @staticmethod
    async def _call_handler(
        func: Callable, *args, error_map: dict[type, Callable] = None, **kwargs
    ) -> Any:
        """
        call a function with error handling, supporting both synchronous and asynchronous
        functions.

        Args:
                func (Callable):
                        The function to call.
                *args:
                        Positional arguments to pass to the function.
                error_map (Dict[type, Callable], optional):
                        A dictionary mapping error types to handler functions.
                **kwargs:
                        Keyword arguments to pass to the function.

        Returns:
                Any: The result of the function call.

        Raises:
                Exception: Propagates any exceptions not handled by the error_map.

        examples:
                >>> async def async_add(x, y): return x + y
                >>> asyncio.run(_call_handler(async_add, 1, 2))
                3
        """
        try:
            if not AsyncUtil.is_coroutine_func(func):
                return func(*args, **kwargs)

            # Checking for a running event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:  # No running event loop
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(func(*args, **kwargs))

                loop.close()
                return result

            if loop.is_running():
                return await func(*args, **kwargs)

        except Exception as e:
            if error_map:
                AsyncUtil._custom_error_handler(e, error_map)
            else:
                logging.error(f"Error in call_handler: {e}")
            raise

    @staticmethod
    @lru_cache(maxsize=None)
    def is_coroutine_func(func: Callable[..., Any]) -> bool:
        """
        Checks whether a function is an asyncio coroutine function.

        Args:
                func: The function to check.

        Returns:
                True if the function is a coroutine function, False otherwise.
        """
        return asyncio.iscoroutinefunction(func)

    @staticmethod
    def _custom_error_handler(
        error: Exception, error_map: Mapping[type, Callable]
    ) -> None:
        # noinspection PyUnresolvedReferences
        """
        handle errors based on a given error mapping.

        Args:
                error (Exception):
                        The error to handle.
                error_map (Mapping[type, Callable]):
                        A dictionary mapping error types to handler functions.

        examples:
                >>> def handle_value_error(e): print("ValueError occurred")
                >>> custom_error_handler(ValueError(), {ValueError: handle_value_error})
                ValueError occurred
        """
        if handler := error_map.get(type(error)):
            handler(error)
        else:
            logging.error(f"Unhandled error: {error}")

    @staticmethod
    async def handle_async_sync(
        func: Callable[..., Any], *args, error_map=None, **kwargs
    ) -> Any:
        """
        Executes a function, automatically handling synchronous and asynchronous functions.

        Args:
                func: The function to execute.
                *args: Positional arguments for the function.
                **kwargs: Keyword arguments for the function.

        Returns:
                The result of the function execution.
        """

        try:
            if not AsyncUtil.is_coroutine_func(func):
                return func(*args, **kwargs)

            try:
                loop = asyncio.get_event_loop()

                return (
                    await func(*args, **kwargs)
                    if loop.is_running()
                    else await asyncio.run(func(*args, **kwargs))
                )
            except RuntimeError:
                return asyncio.run(func(*args, **kwargs))

        except Exception as e:
            if error_map:
                AsyncUtil._custom_error_handler(e, error_map)
            else:
                logging.error(f"Error in call_handler: {e}")
            raise

    @staticmethod
    async def execute_tasks(*tasks):
        if isinstance(tasks[0], (asyncio.Future, Coroutine)):
            return await asyncio.gather(*tasks)
        else:
            return tasks

    @staticmethod
    async def sleep(seconds):
        await asyncio.sleep(seconds)

    # @staticmethod
    # async def execute_timeout(coro, timeout):
    #     return

    # @classmethod
    # def TimeoutError(cls):
    #     return asyncio.TimeoutError

    # @classmethod
    # def CancelledError(cls):
    #     return asyncio.CancelledError

    @classmethod
    def Task(cls):
        return asyncio.Task

    @classmethod
    def Event(cls):
        return asyncio.Event

    @classmethod
    def Lock(cls):
        return asyncio.Lock

    @staticmethod
    def wrap_future(future_):
        return asyncio.wrap_future(future_)

    @staticmethod
    def semaphore(limit):
        return asyncio.Semaphore(limit)

    @staticmethod
    def cached(*args, **kwargs):
        return aiocache.cached(*args, **kwargs)

    @staticmethod
    def create_event(*args, **kwargs):
        return asyncio.Event(*args, **kwargs)

    @staticmethod
    def create_task(*args, obj=True, **kwargs):
        if obj:
            return asyncio.Task(*args, **kwargs)
        else:
            return asyncio.create_task(*args, **kwargs)

    @staticmethod
    def create_lock(*args, **kwargs):
        return asyncio.Lock(*args, **kwargs)

    # @classmethod  # def HttpClientSession(cls):  #     return aiohttp.ClientSession

    # @classmethod  # def HttpClientError(cls):  #     return aiohttp.ClientError
