"""
This module provides a parallel call mechanism for executing multiple functions
asynchronously with options such as retries, initial delay, backoff factor,
timeout, error handling, and throttling.

Functions:
- pcall: Execute multiple functions asynchronously with customizable options.
"""

import asyncio
from typing import Callable, Any, List, Dict, Optional
from lionagi.os.libs.function_handlers._ucall import ucall
from lionagi.os.libs.function_handlers._util import is_coroutine_func


async def pcall(
    funcs: List[Callable[..., Any]],
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = ...,
    timeout: Optional[float] = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: Optional[str] = None,
    error_map: Optional[Dict[type, Callable]] = None,
    max_concurrent: Optional[int] = None,
    throttle_period: Optional[float] = None,
    **kwargs: Any,
) -> List[Any]:
    """
    Execute multiple functions asynchronously with customizable options.

    This function allows executing multiple functions in parallel with support
    for retries, initial delay, backoff factor, timeout, error handling,
    concurrency control, and throttling.

    Args:
        funcs (List[Callable[..., Any]]): List of functions to be executed.
        retries (int, optional): Number of retry attempts for each function.
            Defaults to 0.
        initial_delay (float, optional): Initial delay before starting the
            execution. Defaults to 0.
        delay (float, optional): Delay between retry attempts. Defaults to 0.
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
        error_map (Optional[Dict[type, Callable]], optional): A dictionary
            mapping exception types to error handling functions. Defaults to
            None.
        max_concurrent (Optional[int], optional): Maximum number of concurrent
            executions. Defaults to None.
        throttle_period (Optional[float], optional): Minimum time period
            between successive function executions. Defaults to None.
        **kwargs (Any): Additional keyword arguments to pass to each function.

    Returns:
        List[Any]: The results of the function calls, optionally including the
            duration of execution if `timing` is True.
    """
    if initial_delay:
        await asyncio.sleep(initial_delay)

    semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
    throttle_delay = throttle_period if throttle_period else 0

    async def _task(func: Callable[..., Any], index: int) -> Any:
        if semaphore:
            async with semaphore:
                return await _execute_task(func, index)
        else:
            return await _execute_task(func, index)

    async def _execute_task(func: Callable[..., Any], index: int) -> Any:
        attempts = 0
        current_delay = delay
        while True:
            try:
                if timing:
                    start_time = asyncio.get_event_loop().time()
                    result = await asyncio.wait_for(ucall(func, **kwargs), timeout)
                    end_time = asyncio.get_event_loop().time()
                    return index, result, end_time - start_time
                else:
                    result = await asyncio.wait_for(ucall(func, **kwargs), timeout)
                    return index, result
            except asyncio.TimeoutError as e:
                raise asyncio.TimeoutError(
                    f"{error_msg or ''} Timeout {timeout} seconds exceeded"
                ) from e
            except Exception as e:
                if error_map and type(e) in error_map:
                    handler = error_map[type(e)]
                    if is_coroutine_func(handler):
                        return index, await handler(e)
                    else:
                        return index, handler(e)
                attempts += 1
                if attempts <= retries:
                    if verbose:
                        print(
                            f"Attempt {attempts}/{retries + 1} failed: {e}, retrying..."
                        )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
                else:
                    if default is not ...:
                        return index, default
                    raise e

    tasks = [_task(func, index) for index, func in enumerate(funcs)]
    results = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        await asyncio.sleep(throttle_delay)

    results.sort(key=lambda x: x[0])  # Sort results based on the original index

    if timing:
        return [(result[1], result[2]) for result in results]
    else:
        return [result[1] for result in results]
