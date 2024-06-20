"""
This module provides a utility to execute functions asynchronously with various
options such as delay, error handling, timeout, and execution timing.

Functions:
- tcall: Execute a function asynchronously with customizable options.
"""

import asyncio
from typing import Any, Callable, Optional, Dict


async def tcall(
    func: Callable[..., Any],
    *args: Any,
    initial_delay: float = 0,
    error_msg: Optional[str] = None,
    suppress_err: bool = False,
    timing: bool = False,
    timeout: Optional[float] = None,
    default: Any = None,
    error_map: Optional[Dict[type, Callable[[Exception], None]]] = None,
    **kwargs: Any,
) -> Any:
    """
    Execute a function asynchronously with customizable options.

    This function can handle both synchronous and asynchronous functions,
    applying an initial delay, timing the execution, handling errors, and
    enforcing a timeout.

    Args:
        func (Callable[..., Any]): The function to be executed.
        *args (Any): Positional arguments to pass to the function.
        initial_delay (float, optional): Delay before executing the function.
            Defaults to 0.
        error_msg (Optional[str], optional): Custom error message. Defaults to
            None.
        suppress_err (bool, optional): Whether to suppress errors and return a
            default value. Defaults to False.
        timing (bool, optional): Whether to return the execution duration.
            Defaults to False.
        timeout (Optional[float], optional): Timeout for the function
            execution. Defaults to None.
        default (Any, optional): Default value to return if an error occurs.
            Defaults to None.
        error_map (Optional[Dict[type, Callable[[Exception], None]]], optional):
            A dictionary mapping exception types to error handling functions.
            Defaults to None.
        **kwargs (Any): Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, optionally including the duration
            of execution if `timing` is True.

    Raises:
        asyncio.TimeoutError: If the function execution exceeds the timeout.
        RuntimeError: If an error occurs and `suppress_err` is False.
    """
    start = asyncio.get_event_loop().time()

    try:
        await asyncio.sleep(initial_delay)
        result = None

        if asyncio.iscoroutinefunction(func):
            # Asynchronous function
            if timeout is None:
                result = await func(*args, **kwargs)
            else:
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        else:
            # Synchronous function
            if timeout is None:
                result = func(*args, **kwargs)
            else:
                result = await asyncio.wait_for(
                    asyncio.shield(asyncio.to_thread(func, *args, **kwargs)),
                    timeout=timeout,
                )

        duration = asyncio.get_event_loop().time() - start
        return (result, duration) if timing else result

    except asyncio.TimeoutError as e:
        error_msg = f"{error_msg or ''} Timeout {timeout} seconds exceeded"
        if suppress_err:
            duration = asyncio.get_event_loop().time() - start
            return (default, duration) if timing else default
        else:
            raise asyncio.TimeoutError(error_msg) from e

    except Exception as e:
        if error_map and type(e) in error_map:
            error_map[type(e)](e)
            duration = asyncio.get_event_loop().time() - start
            return (None, duration) if timing else None
        error_msg = (
            f"{error_msg} Error: {e}"
            if error_msg
            else f"An error occurred in async execution: {e}"
        )
        if suppress_err:
            duration = asyncio.get_event_loop().time() - start
            return (default, duration) if timing else default
        else:
            raise RuntimeError(error_msg) from e
