"""
This module provides a list call mechanism to apply a function over a list of
inputs asynchronously with options such as retries, initial delay, backoff
factor, timeout, error handling, and throttling.

Functions:
- lcall: Apply a function over a list of inputs asynchronously with
  customizable options.
"""

import asyncio
from typing import Any, Callable, List, Dict, Optional
from lionagi.os.libs.data_handlers import to_list
from lionagi.os.libs.function_handlers._ucall import ucall


async def lcall(
    func: Callable[..., Any],
    input_: List[Any],
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = ...,
    timeout: Optional[float] = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: Optional[str] = None,
    error_map: Optional[Dict[type, Callable[[Exception], Any]]] = None,
    max_concurrent: Optional[int] = None,
    throttle_period: Optional[float] = None,
    flatten: bool = False,
    dropna: bool = False,
    **kwargs: Any,
) -> List[Any]:
    """
    Apply a function over a list of inputs asynchronously with customizable
    options.

    This function allows executing a function over a list of inputs in parallel
    with support for retries, initial delay, backoff factor, timeout, error
    handling, concurrency control, and throttling.

    Args:
        func (Callable[..., Any]): The function to be applied to each input.
        input_ (List[Any]): List of inputs to be processed.
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
        error_map (Optional[Dict[type, Callable[[Exception], Any]]], optional):
            A dictionary mapping exception types to error handling functions.
            Defaults to None.
        max_concurrent (Optional[int], optional): Maximum number of concurrent
            executions. Defaults to None.
        throttle_period (Optional[float], optional): Minimum time period
            between successive function executions. Defaults to None.
        flatten (bool, optional): Whether to flatten the output list. Defaults
            to False.
        dropna (bool, optional): Whether to drop None values from the output
            list. Defaults to False.
        **kwargs (Any): Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: The results of the function calls, optionally including the
            duration of execution if `timing` is True.
    """
    if initial_delay:
        await asyncio.sleep(initial_delay)

    semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
    throttle_delay = throttle_period if throttle_period else 0

    async def _task(i: Any, index: int) -> Any:
        if semaphore:
            async with semaphore:
                return await _execute_task(i, index)
        else:
            return await _execute_task(i, index)

    async def _execute_task(i: Any, index: int) -> Any:
        attempts = 0
        current_delay = delay
        while True:
            try:
                if timing:
                    start_time = asyncio.get_event_loop().time()
                    result = await asyncio.wait_for(ucall(func, i, **kwargs), timeout)
                    end_time = asyncio.get_event_loop().time()
                    return index, result, end_time - start_time
                else:
                    result = await asyncio.wait_for(ucall(func, i, **kwargs), timeout)
                    return index, result
            except asyncio.TimeoutError as e:
                raise asyncio.TimeoutError(
                    f"{error_msg or ''} Timeout {timeout} seconds exceeded"
                ) from e
            except Exception as e:
                if error_map and type(e) in error_map:
                    handler = error_map[type(e)]
                    if asyncio.iscoroutinefunction(handler):
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

    tasks = [_task(i, index) for index, i in enumerate(input_)]
    results = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        await asyncio.sleep(throttle_delay)

    results.sort(key=lambda x: x[0])  # Sort results based on the original index

    if timing:
        if not flatten:
            if dropna:
                return [
                    (result[1], result[2])
                    for result in results
                    if result[1] is not None
                ]
            else:
                return [(result[1], result[2]) for result in results]
        else:
            return to_list([result[1] for result in results], dropna=dropna)
    else:
        return [result[1] for result in results]
