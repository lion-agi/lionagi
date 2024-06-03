"""
This module provides a retry mechanism for function calls with options such as
initial delay, backoff factor, timeout, and error handling.

Functions:
- rcall: Retry a function asynchronously with customizable options.
- _rcall: Helper function for rcall to handle the core logic.
"""

import asyncio
from typing import Any, Callable, Optional, Dict
from lionagi.os.libs.sys_util import get_now
from lionagi.os.libs.function_handlers._ucall import ucall


async def rcall(
    func: Callable[..., Any],
    *args: Any,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = ...,
    timeout: Optional[float] = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: Optional[str] = None,
    error_map: Optional[Dict[type, Callable[[Exception], None]]] = None,
    **kwargs: Any,
) -> Any:
    """
    Retry a function asynchronously with customizable options.

    This function attempts to execute the given function multiple times based
    on the retry configuration. It supports options like initial delay, backoff
    factor, timeout, error handling, and execution timing.

    Args:
        func (Callable[..., Any]): The function to be executed.
        *args (Any): Positional arguments to pass to the function.
        retries (int, optional): Number of retry attempts. Defaults to 0.
        initial_delay (float, optional): Initial delay before the first attempt.
            Defaults to 0.
        delay (float, optional): Delay between attempts. Defaults to 0.
        backoff_factor (float, optional): Factor by which the delay increases
            after each attempt. Defaults to 1.
        default (Any, optional): Default value to return if all attempts fail.
            Defaults to ... (ellipsis).
        timeout (Optional[float], optional): Timeout for each function
            execution. Defaults to None.
        timing (bool, optional): Whether to return the execution duration.
            Defaults to False.
        verbose (bool, optional): Whether to print retry messages. Defaults to
            True.
        error_msg (Optional[str], optional): Custom error message. Defaults to
            None.
        error_map (Optional[Dict[type, Callable[[Exception], None]]], optional):
            A dictionary mapping exception types to error handling functions.
            Defaults to None.
        **kwargs (Any): Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, optionally including the duration
            of execution if `timing` is True.

    Raises:
        RuntimeError: If the function fails after the specified number of
            retries.
    """
    last_exception = None
    result = None

    await asyncio.sleep(initial_delay)

    for attempt in range(retries + 1):
        try:
            if retries == 0:
                if timing:
                    result, duration = await _rcall(
                        func, *args, timeout=timeout, timing=True, **kwargs
                    )
                    return result, duration

                result = await _rcall(func, *args, timeout=timeout, **kwargs)
                return result
            err_msg = f"Attempt {attempt + 1}/{retries + 1}: {error_msg or ''}"
            if timing:
                result, duration = await _rcall(
                    func, *args, err_msg=err_msg, timeout=timeout, timing=True, **kwargs
                )
                return result, duration

            result = await _rcall(
                func, *args, err_msg=err_msg, timeout=timeout, **kwargs
            )
            return result
        except Exception as e:
            last_exception = e
            if error_map and type(e) in error_map:
                error_map[type(e)](e)
            if attempt < retries:
                if verbose:
                    print(
                        f"Attempt {attempt + 1}/{retries + 1} failed: {e}, retrying..."
                    )
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                break

    if default is not ...:
        return default

    if last_exception is not None:
        if error_map and type(last_exception) in error_map:
            handler = error_map[type(last_exception)]
            if asyncio.iscoroutinefunction(handler):
                return await handler(last_exception)
            else:
                return handler(last_exception)
        raise RuntimeError(
            f"{error_msg or ''} Operation failed after {retries + 1} attempts: {last_exception}"
        ) from last_exception

    raise RuntimeError(
        f"{error_msg or ''} Operation failed after {retries + 1} attempts"
    )


async def _rcall(
    func: Callable[..., Any],
    *args: Any,
    delay: float = 0,
    err_msg: Optional[str] = None,
    ignore_err: bool = False,
    timing: bool = False,
    default: Any = None,
    timeout: Optional[float] = None,
    **kwargs: Any,
) -> Any:
    """
    Helper function for rcall to handle the core logic.

    Args:
        func (Callable[..., Any]): The function to be executed.
        *args (Any): Positional arguments to pass to the function.
        delay (float, optional): Delay before executing the function. Defaults
            to 0.
        err_msg (Optional[str], optional): Custom error message. Defaults to
            None.
        ignore_err (bool, optional): Whether to ignore errors and return a
            default value. Defaults to False.
        timing (bool, optional): Whether to return the execution duration.
            Defaults to False.
        default (Any, optional): Default value to return if an error occurs.
            Defaults to None.
        timeout (Optional[float], optional): Timeout for the function
            execution. Defaults to None.
        **kwargs (Any): Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, optionally including the duration
            of execution if `timing` is True.

    Raises:
        asyncio.TimeoutError: If the function execution exceeds the timeout.
        Exception: If an error occurs and `ignore_err` is False.
    """
    start_time = get_now(datetime_=False)
    try:
        await asyncio.sleep(delay)
        if timeout is not None:
            result = await asyncio.wait_for(ucall(func, *args, **kwargs), timeout)
        else:
            result = await ucall(func, *args, **kwargs)
        duration = get_now(datetime_=False) - start_time
        return (result, duration) if timing else result
    except asyncio.TimeoutError as e:
        err_msg = f"{err_msg or ''} Timeout {timeout} seconds exceeded"
        if ignore_err:
            duration = get_now(datetime_=False) - start_time
            return (default, duration) if timing else default
        else:
            raise asyncio.TimeoutError(err_msg) from e
    except Exception as e:
        if ignore_err:
            duration = get_now(datetime_=False) - start_time
            return (default, duration) if timing else default
        else:
            raise
