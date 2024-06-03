"""
This module provides utilities for converting synchronous functions to
asynchronous ones, checking if a function is a coroutine, handling errors
customly, limiting concurrency, and throttling function execution.

The following functionalities are provided:
- force_async: Convert a synchronous function to an asynchronous function.
- is_coroutine_func: Check if a function is a coroutine function.
- custom_error_handler: Handle errors based on a custom error map.
- max_concurrent: Limit the concurrency of function execution.
- throttle: Throttle function execution to limit the rate of calls.
"""

import logging
import asyncio
from typing import Any, Callable, Dict
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor
from lionagi.os.libs.function_handlers._throttle import Throttle


def force_async(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Convert a synchronous function to an asynchronous function using a thread
    pool.

    Args:
        fn (Callable[..., Any]): The synchronous function to convert.

    Returns:
        Callable[..., Any]: The asynchronous version of the function.
    """
    pool = ThreadPoolExecutor()

    @wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # Make it awaitable

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
    Handle errors based on a custom error map.

    Args:
        error (Exception): The error that occurred.
        error_map (Dict[type, Callable]): A map of error types to handler
            functions.
    """
    for error_type, handler in error_map.items():
        if isinstance(error, error_type):
            handler(error)
            return
    logging.error(f"Unhandled error: {error}")


def max_concurrent(func: Callable, limit: int) -> Callable:
    """
    Limit the concurrency of function execution using a semaphore.

    Args:
        func (Callable): The function to limit concurrency for.
        limit (int): The maximum number of concurrent executions.

    Returns:
        Callable: The function wrapped with concurrency control.
    """
    if not is_coroutine_func(func):
        func = force_async(func)
    semaphore = asyncio.Semaphore(limit)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with semaphore:
            return await func(*args, **kwargs)

    return wrapper


def throttle(func: Callable, period: float) -> Callable:
    """
    Throttle function execution to limit the rate of calls.

    Args:
        func (Callable): The function to throttle.
        period (float): The minimum time interval between consecutive calls.

    Returns:
        Callable: The throttled function.
    """
    if not is_coroutine_func(func):
        func = force_async(func)
    throttle_instance = Throttle(period)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        await throttle_instance(func)(*args, **kwargs)
        return await func(*args, **kwargs)

    return wrapper
