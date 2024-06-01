from typing import Any, Callable
import asyncio
from ..sys_util import get_now
from ._ucall import ucall


async def tcall(
    func: Callable,
    *args,
    initial_delay: float = 0,
    err_msg: str | None = None,
    suppress_err: bool = False,
    timing: bool = False,
    timeout: float | None = None,
    default: Any = None,
    **kwargs,
) -> Any:
    """
    Asynchronously call a function with optional delay, error handling, timing,
    and timeout.

    This function calls the given function asynchronously, with support for
    initial delay, error suppression, timing, and timeout.

    Args:
        func (Callable): The function to call.
        *args: Positional arguments to pass to the function.
        initial_delay (float, optional): Initial delay before the function call
            in seconds. Defaults to 0.
        err_msg (str | None, optional): Custom error message prefix. Defaults
            to None.
        suppress_err (bool, optional): If True, suppresses errors and returns
            a default value. Defaults to False.
        timing (bool, optional): If True, return the execution time along with
            the result. Defaults to False.
        timeout (float | None, optional): Timeout for the function call in
            seconds. Defaults to None.
        default (Any, optional): The default value to return if an error occurs
            and suppress_err is True. Defaults to None.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, or the default value if an error
            occurs and suppress_err is True. If timing is True, returns a tuple
            of (result, duration).

    Raises:
        asyncio.TimeoutError: If the function call exceeds the timeout.
        RuntimeError: If an error occurs and suppress_err is False.

    Examples:
        >>> async def sample_func(x):
        >>>     await asyncio.sleep(1)
        >>>     return x * 2
        >>>
        >>> result = await tcall(sample_func, 5, timeout=2)
        >>> print(result)
    """
    start = get_now(datetime_=False)

    try:
        await asyncio.sleep(initial_delay)
        result = None

        if timeout is None:
            result = await ucall(func, *args, **kwargs)
        else:
            try:
                result = await asyncio.wait_for(
                    ucall(func, *args, **kwargs), timeout=timeout
                )
            except asyncio.TimeoutError as e:
                err_msg = f"{err_msg or ''}Timeout {timeout} seconds exceeded"
                if suppress_err:
                    duration = get_now(datetime_=False) - start
                    return (default, duration) if timing else default
                else:
                    raise asyncio.TimeoutError(err_msg)

        duration = get_now(datetime_=False) - start
        return (result, duration) if timing else result

    except Exception as e:
        err_msg = (
            f"{err_msg} Error: {e}"
            if err_msg
            else f"An error occurred in async execution: {e}"
        )
        if suppress_err:
            duration = get_now(datetime_=False) - start
            return (default, duration) if timing else default
        else:
            raise RuntimeError(err_msg)
