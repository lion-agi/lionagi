from typing import Any, Callable
import asyncio
from ..data_handlers import to_list
from ._rcall import rcall
from ._util import max_concurrency, throttle


async def lcall(
    func: Callable,  # Function to call
    input_: list[Any],  # List of inputs
    retries: int = 0,  # Number of retries
    initial_delay: float = 0,  # Initial delay before the first call
    delay: float = 0.1,  # Delay between retries
    backoff_factor: float = 2,  # Backoff factor for delay
    default: Any = None,  # Default value to return if an error occurs
    timeout: float | None = None,  # Timeout for the function call in seconds
    timing: bool = False,  # Return the execution time along with the result
    verbose: bool = True,  # Print retry attempts and exceptions
    error_msg: str | None = None,  # Custom error message prefix
    error_map: dict | None = None,  # Error mapping
    max_concurrent: int | None = None,  # Maximum number of concurrent calls
    throttle_period: float | None = None,  # Throttle period
    **kwargs,
) -> list[Any]:
    """
    Asynchronously call a function for each input in the list with retry logic,
    optional timing, concurrency, and throttling.

    Args:
        func (Callable): The function to call.
        input_ (list[Any]): List of inputs to process.
        retries (int, optional): The number of retries. Defaults to 0.
        initial_delay (float, optional): Initial delay before the first attempt
            in seconds. Defaults to 0.
        delay (float, optional): The delay between retries in seconds.
            Defaults to 0.1.
        backoff_factor (float, optional): The factor by which the delay is
            multiplied after each retry. Defaults to 2.
        default (Any, optional): The default value to return if an error occurs
            and suppress_err is True. Defaults to None.
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
        max_concurrent (int | None, optional): Maximum number of concurrent
            calls. Defaults to None.
        throttle_period (float | None, optional): Throttle period in seconds.
            Defaults to None.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        list[Any]: A list of results from the function calls.

    Examples:
        >>> async def sample_func(x):
        >>>     return x * 2
        >>>
        >>> results = await lcall(sample_func, [1, 2, 3], retries=3, delay=1)
        >>> print(results)
    """

    async def _task(i):
        return await rcall(
            func,
            i,
            retries=retries,
            initial_delay=initial_delay,
            delay=delay,
            backoff_factor=backoff_factor,
            default=default,
            timeout=timeout,
            timing=timing,
            verbose=verbose,
            error_msg=error_msg,
            error_map=error_map,
            **kwargs,
        )

    if max_concurrent:
        _task = max_concurrency(_task, max_concurrent)

    if throttle_period:
        _task = throttle(_task, throttle_period)

    tasks = [_task(i) for i in to_list(input_)]
    outs = await asyncio.gather(*tasks)
    return to_list(outs)
