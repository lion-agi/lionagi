import asyncio
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from lionagi.libs.func.utils import is_coroutine_func

from ...constants import UNDEFINED
from .ucall import ucall

T = TypeVar("T")


async def pcall(
    funcs: Sequence[Callable[..., T]],
    /,
    num_retries: int = 0,
    initial_delay: float = 0,
    retry_delay: float = 0,
    backoff_factor: float = 1,
    retry_default: Any = UNDEFINED,
    retry_timeout: float | None = None,
    retry_timing: bool = False,
    verbose_retry: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, Callable[[Exception], None]] | None = None,
    max_concurrent: int | None = None,
    throttle_period: float | None = None,
    **kwargs: Any,
) -> list[T] | list[tuple[T, float]]:
    """Execute multiple functions asynchronously in parallel with options.

    Manages parallel execution of functions with retry logic, timing, and
    error handling. Supports concurrency control and throttling.

    Args:
        funcs: Sequence of functions to execute in parallel.
        num_retries: Number of retry attempts for each function (default: 0).
        initial_delay: Delay before starting execution (seconds).
        retry_delay: Initial delay between retry attempts (seconds).
        backoff_factor: Factor to increase delay after each retry.
        retry_default: Value to return if all attempts for a function fail.
        retry_timeout: Timeout for each function execution (seconds).
        retry_timing: If True, return execution duration for each function.
        verbose_retry: If True, print retry messages.
        error_msg: Custom error message prefix.
        error_map: Dict mapping exception types to error handlers.
        max_concurrent: Maximum number of functions to run concurrently.
        throttle_period: Minimum time between function starts (seconds).
        **kwargs: Additional keyword arguments passed to each function.

    Returns:
        list[T] | list[tuple[T, float]]: List of results, optionally with
        execution times if retry_timing is True.

    Raises:
        asyncio.TimeoutError: If any function execution exceeds retry_timeout.
        Exception: Any unhandled exception from function executions.

    Examples:
        >>> async def func1(x):
        ...     await asyncio.sleep(1)
        ...     return x * 2
        >>> async def func2(x):
        ...     await asyncio.sleep(0.5)
        ...     return x + 10
        >>> results = await pcall([func1, func2], retry_timing=True, x=5)
        >>> for result, duration in results:
        ...     print(f"Result: {result}, Duration: {duration:.2f}s")
        Result: 10, Duration: 1.00s
        Result: 15, Duration: 0.50s

    Note:
        - Executes functions in parallel, respecting max_concurrent limit.
        - Implements exponential backoff for retries.
        - Can return execution timing for performance analysis.
        - Supports both coroutine and regular functions via ucall.
        - Results are returned in the original order of input functions.
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
        current_delay = retry_delay
        while True:
            try:
                if retry_timing:
                    start_time = asyncio.get_event_loop().time()
                    result = await asyncio.wait_for(
                        ucall(func, **kwargs), retry_timeout
                    )
                    end_time = asyncio.get_event_loop().time()
                    return index, result, end_time - start_time
                else:
                    result = await asyncio.wait_for(
                        ucall(func, **kwargs), retry_timeout
                    )
                    return index, result
            except TimeoutError as e:
                raise TimeoutError(
                    f"{error_msg or ''} Timeout {retry_timeout} seconds "
                    "exceeded"
                ) from e
            except Exception as e:
                if error_map and type(e) in error_map:
                    handler = error_map[type(e)]
                    if is_coroutine_func(handler):
                        return index, await handler(e)
                    else:
                        return index, handler(e)
                attempts += 1
                if attempts <= num_retries:
                    if verbose_retry:
                        print(
                            f"Attempt {attempts}/{num_retries + 1} failed: {e}"
                            ", retrying..."
                        )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
                else:
                    if retry_default is not UNDEFINED:
                        return index, retry_default
                    raise e

    tasks = [_task(func, index) for index, func in enumerate(funcs)]
    results = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        await asyncio.sleep(throttle_delay)

    results.sort(
        key=lambda x: x[0]
    )  # Sort results based on the original index

    if retry_timing:
        return [(result[1], result[2]) for result in results]
    else:
        return [result[1] for result in results]
