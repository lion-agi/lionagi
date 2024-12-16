import asyncio
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from ...constants import UNDEFINED
from .ucall import ucall

T = TypeVar("T")


async def tcall(
    func: Callable[..., T],
    /,
    *args: Any,
    initial_delay: float = 0,
    error_msg: str | None = None,
    suppress_err: bool = False,
    retry_timing: bool = False,
    retry_timeout: float | None = None,
    retry_default: Any = None,
    error_map: dict[type, Callable[[Exception], None]] | None = None,
    **kwargs: Any,
) -> T | tuple[T, float]:
    """Execute a function asynchronously with timing and error handling.

    Handles both coroutine and regular functions, supporting timing,
    timeout, and custom error handling.

    Args:
        func: The function to execute (coroutine or regular).
        *args: Positional arguments for the function.
        initial_delay: Delay before execution (seconds).
        error_msg: Custom error message prefix.
        suppress_err: If True, return default on error instead of raising.
        retry_timing: If True, return execution duration.
        retry_timeout: Timeout for function execution (seconds).
        retry_default: Value to return if an error occurs and suppress_err
        is True.
        error_map: Dict mapping exception types to error handlers.
        **kwargs: Additional keyword arguments for the function.

    Returns:
        T | tuple[T, float]: Function result, optionally with duration.

    Raises:
        asyncio.TimeoutError: If execution exceeds the timeout.
        RuntimeError: If an error occurs and suppress_err is False.

    Examples:
        >>> async def slow_func(x):
        ...     await asyncio.sleep(1)
        ...     return x * 2
        >>> result, duration = await tcall(slow_func, 5, retry_timing=True)
        >>> print(f"Result: {result}, Duration: {duration:.2f}s")
        Result: 10, Duration: 1.00s

    Note:
        - Automatically handles both coroutine and regular functions.
        - Provides timing information for performance analysis.
        - Supports custom error handling and suppression.
    """
    start = asyncio.get_event_loop().time()

    try:
        await asyncio.sleep(initial_delay)
        result = None

        if asyncio.iscoroutinefunction(func):
            # Asynchronous function
            if retry_timeout is None:
                result = await func(*args, **kwargs)
            else:
                result = await asyncio.wait_for(
                    func(*args, **kwargs), timeout=retry_timeout
                )
        else:
            # Synchronous function
            if retry_timeout is None:
                result = func(*args, **kwargs)
            else:
                result = await asyncio.wait_for(
                    asyncio.shield(asyncio.to_thread(func, *args, **kwargs)),
                    timeout=retry_timeout,
                )

        duration = asyncio.get_event_loop().time() - start
        return (result, duration) if retry_timing else result

    except TimeoutError as e:
        error_msg = (
            f"{error_msg or ''} Timeout {retry_timeout} seconds exceeded"
        )
        if suppress_err:
            duration = asyncio.get_event_loop().time() - start
            return (retry_default, duration) if retry_timing else retry_default
        else:
            raise TimeoutError(error_msg) from e

    except Exception as e:
        if error_map and type(e) in error_map:
            error_map[type(e)](e)
            duration = asyncio.get_event_loop().time() - start
            return (None, duration) if retry_timing else None
        error_msg = (
            f"{error_msg} Error: {e}"
            if error_msg
            else f"An error occurred in async execution: {e}"
        )
        if suppress_err:
            duration = asyncio.get_event_loop().time() - start
            return (retry_default, duration) if retry_timing else retry_default
        else:
            raise RuntimeError(error_msg) from e
