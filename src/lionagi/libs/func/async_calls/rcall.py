import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

from ...constants import UNDEFINED
from ...utils import time as _t
from .ucall import ucall

T = TypeVar("T")


async def rcall(
    func: Callable[..., T],
    /,
    *args: Any,
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
    **kwargs: Any,
) -> T | tuple[T, float]:
    """Retry a function asynchronously with customizable options.

    Executes a function with specified retry logic, timing, and error handling.

    Args:
        func: The function to execute (coroutine or regular).
        *args: Positional arguments for the function.
        num_retries: Number of retry attempts (default: 0).
        initial_delay: Delay before first attempt (seconds).
        retry_delay: Delay between retry attempts (seconds).
        backoff_factor: Factor to increase delay after each retry.
        retry_default: Value to return if all attempts fail.
        retry_timeout: Timeout for each function execution (seconds).
        retry_timing: If True, return execution duration.
        verbose_retry: If True, print retry messages.
        error_msg: Custom error message prefix.
        error_map: Dict mapping exception types to error handlers.
        **kwargs: Additional keyword arguments for the function.

    Returns:
        T | tuple[T, float]: Function result, optionally with duration.

    Raises:
        RuntimeError: If function fails after all retries.
        asyncio.TimeoutError: If execution exceeds retry_timeout.

    Examples:
        >>> async def flaky_func(x):
        ...     if random.random() < 0.5:
        ...         raise ValueError("Random failure")
        ...     return x * 2
        >>> result = await rcall(flaky_func, 5, num_retries=3)
        >>> print(result)
        10

    Note:
        - Supports both coroutine and regular functions.
        - Implements exponential backoff for retries.
        - Can return execution timing for performance analysis.
    """
    last_exception = None
    result = None

    await asyncio.sleep(initial_delay)
    for attempt in range(num_retries + 1):
        try:
            if num_retries == 0:
                if retry_timing:
                    result, duration = await _rcall(
                        func,
                        *args,
                        retry_timeout=retry_timeout,
                        retry_timing=True,
                        **kwargs,
                    )
                    return result, duration
                result = await _rcall(
                    func,
                    *args,
                    retry_timeout=retry_timeout,
                    **kwargs,
                )
                return result
            err_msg = (
                f"Attempt {attempt + 1}/{num_retries + 1}: {error_msg or ''}"
            )
            if retry_timing:
                result, duration = await _rcall(
                    func,
                    *args,
                    error_msg=err_msg,
                    retry_timeout=retry_timeout,
                    retry_timing=True,
                    **kwargs,
                )
                return result, duration

            result = await _rcall(
                func,
                *args,
                error_msg=err_msg,
                retry_timeout=retry_timeout,
                **kwargs,
            )
            return result
        except Exception as e:
            last_exception = e
            if error_map and type(e) in error_map:
                error_map[type(e)](e)
            if attempt < num_retries:
                if verbose_retry:
                    print(
                        f"Attempt {attempt + 1}/{num_retries + 1} failed: {e},"
                        " retrying..."
                    )
                await asyncio.sleep(retry_delay)
                retry_delay *= backoff_factor
            else:
                break

    if retry_default is not UNDEFINED:
        return retry_default

    if last_exception is not None:
        if error_map and type(last_exception) in error_map:
            handler = error_map[type(last_exception)]
            if asyncio.iscoroutinefunction(handler):
                return await handler(last_exception)
            else:
                return handler(last_exception)
        raise RuntimeError(
            f"{error_msg or ''} Operation failed after {num_retries + 1} "
            f"attempts: {last_exception}"
        ) from last_exception

    raise RuntimeError(
        f"{error_msg or ''} Operation failed after {num_retries + 1} attempts"
    )


async def _rcall(
    func: Callable[..., T],
    *args: Any,
    retry_delay: float = 0,
    error_msg: str | None = None,
    ignore_err: bool = False,
    retry_timing: bool = False,
    retry_default: Any = None,
    retry_timeout: float | None = None,
    **kwargs: Any,
) -> T | tuple[T, float]:
    start_time = _t()

    try:
        await asyncio.sleep(retry_delay)
        if retry_timeout is not None:
            result = await asyncio.wait_for(
                ucall(func, *args, **kwargs), timeout=retry_timeout
            )
        else:
            result = await ucall(func, *args, **kwargs)
        duration = _t() - start_time
        return (result, duration) if retry_timing else result
    except TimeoutError as e:
        error_msg = (
            f"{error_msg or ''} Timeout {retry_timeout} seconds exceeded"
        )
        if ignore_err:
            duration = _t() - start_time
            return (retry_default, duration) if retry_timing else retry_default
        else:
            raise TimeoutError(error_msg) from e
    except Exception:
        if ignore_err:
            duration = _t() - start_time
            return (retry_default, duration) if retry_timing else retry_default
        else:
            raise
