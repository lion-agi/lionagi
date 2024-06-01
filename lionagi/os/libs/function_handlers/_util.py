import logging
import asyncio
from typing import Any, Callable, Dict
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor


def force_async(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Convert a synchronous function to an asynchronous function using a thread pool.

    Args:
        fn (Callable[..., Any]): The synchronous function to convert.

    Returns:
        Callable[..., Any]: The asynchronous version of the function.
    """
    pool = ThreadPoolExecutor()

    @wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # make it awaitable

    return wrapper


@lru_cache(maxsize=None)
def is_coroutine_func(func: Callable) -> bool:
    """
    Check if a function is a coroutine function.

    Args:
        func (Callable): The function to check.

    Returns:
        bool: True if the function is a coroutine function, False otherwise.
    """
    return asyncio.iscoroutinefunction(func)


def custom_error_handler(error: Exception, error_map: Dict[type, Callable]) -> None:
    """
    Handle errors based on a given error mapping.

    Args:
        error (Exception): The error to handle.
        error_map (Dict[type, Callable]): A dictionary mapping error types to
            handler functions.

    Examples:
        >>> def handle_value_error(e): print("ValueError occurred")
        >>> custom_error_handler(ValueError(), {ValueError: handle_value_error})
        ValueError occurred
    """
    if handler := error_map.get(type(error)):
        handler(error)
    else:
        logging.error(f"Unhandled error: {error}")
