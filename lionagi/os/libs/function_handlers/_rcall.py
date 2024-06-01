import asyncio
from typing import Any, Callable
from ..sys_util import get_now
from ._tcall import tcall


async def rcall(
    func: Callable,
    *args,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0.1,
    backoff_factor: float = 2,
    default: Any = None,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict | None = None,
    **kwargs,
) -> Any:
    """
    Asynchronously call a function with retry logic and optional timing.

    This function calls the given function asynchronously, with support for
    retries, exponential backoff, and optional timing of the execution.

    Args:
        func (Callable): The function to call.
        *args: Positional arguments to pass to the function.
        retries (int, optional): The number of retries. Defaults to 0.
        initial_delay (float, optional): Initial delay before the first attempt
            in seconds. Defaults to 0.
        delay (float, optional): The delay between retries in seconds.
            Defaults to 0.1.
        backoff_factor (float, optional): The factor by which the delay is
            multiplied after each retry. Defaults to 2.
        default (Any, optional): The default value to return if all retries
            fail. Defaults to None.
        timeout (float | None, optional): The timeout for the function call in
            seconds. Defaults to None.
        timing (bool, optional): If True, return the execution time along with
            the result. Defaults to False.
        verbose (bool, optional): If True, print retry attempts and exceptions.
            Defaults to True.
        error_msg (str | None, optional): Custom error message prefix. Defaults
            to None.
        error_map (dict | None, optional): Mapping of errors to handle custom
            error responses. Defaults to None.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, or the default value if all
            retries fail. If timing is True, returns a tuple of (result,
            duration).

    Raises:
        RuntimeError: If all retries fail and no default value is provided,
            or if an unexpected error occurs.

    Examples:
        >>> async def sample_func(x):
        >>>     return x * 2
        >>>
        >>> result = await rcall(sample_func, 5, retries=3, delay=1)
        >>> print(result)
    """
    last_exception = None
    result = None
    start = get_now(datetime_=False)
    await asyncio.sleep(initial_delay)

    for attempt in range(retries + 1):
        try:
            attempt_msg = (
                f"Attempt {attempt + 1}/{retries + 1}: " if retries > 0 else None
            )
            full_error_msg = f"{attempt_msg}{error_msg}" if error_msg else attempt_msg
            if timing:
                result, duration = await tcall(
                    func,
                    *args,
                    initial_delay=0,
                    error_msg=full_error_msg,
                    suppress_err=False,
                    timing=True,
                    timeout=timeout,
                    default=None,
                    error_map=error_map,
                    **kwargs,
                )
                return result, duration

            result = await tcall(
                func,
                *args,
                initial_delay=0,
                error_msg=full_error_msg,
                suppress_err=False,
                timing=False,
                timeout=timeout,
                default=None,
                error_map=error_map,
                **kwargs,
            )
            return result

        except Exception as e:
            last_exception = e
            if attempt < retries:
                if verbose:
                    print(
                        f"Attempt {attempt + 1}/{retries + 1} failed: {e}, retrying..."
                    )
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                break

    if result is None and default is not None:
        return default
    elif last_exception is not None:
        raise RuntimeError(
            f"Operation failed after {retries + 1} attempts: {last_exception}"
        ) from last_exception
    else:
        raise RuntimeError("rcall failed without catching an exception")
