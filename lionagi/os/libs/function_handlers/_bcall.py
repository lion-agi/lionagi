"""
This module provides a batch call mechanism to process inputs in batches
asynchronously with options such as retries, initial delay, backoff factor,
timeout, error handling, and throttling.

Functions:
- bcall: Process inputs in batches asynchronously with customizable options.
"""

from typing import Any, Callable, AsyncGenerator, Optional, Dict, List
from lionagi.os.libs.data_handlers import to_list
from lionagi.os.libs.function_handlers._lcall import lcall


async def bcall(
    input_: Any,
    func: Callable[..., Any],
    batch_size: int,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = None,
    timeout: Optional[float] = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: Optional[str] = None,
    error_map: Optional[Dict[type, Callable[[Exception], Any]]] = None,
    max_concurrent: Optional[int] = None,
    throttle_period: Optional[float] = None,
    **kwargs: Any,
) -> AsyncGenerator[List[Any], None]:
    """
    Asynchronously call a function in batches with retry logic, optional
    timing, concurrency, and throttling.

    This function processes inputs in batches, calling the given function
    asynchronously for each batch and supporting retries, exponential backoff,
    and optional timing of the execution.

    Args:
        input_ (Any): The input data to process.
        func (Callable[..., Any]): The function to call.
        batch_size (int): The size of each batch.
        retries (int, optional): The number of retries. Defaults to 0.
        initial_delay (float, optional): Initial delay before the first attempt
            in seconds. Defaults to 0.
        delay (float, optional): The delay between retries in seconds.
            Defaults to 0.
        backoff_factor (float, optional): The factor by which the delay is
            multiplied after each retry. Defaults to 1.
        default (Any, optional): The default value to return if an error occurs
            and suppress_err is True. Defaults to None.
        timeout (Optional[float], optional): The timeout for the function call
            in seconds. Defaults to None.
        timing (bool, optional): If True, return the execution time along with
            the result. Defaults to False.
        verbose (bool, optional): If True, print retry attempts and exceptions.
            Defaults to True.
        error_msg (Optional[str], optional): Custom error message prefix.
            Defaults to None.
        error_map (Optional[Dict[type, Callable[[Exception], Any]]], optional):
            Mapping of errors to handle custom error responses. Defaults to
            None.
        max_concurrent (Optional[int], optional): Maximum number of concurrent
            calls. Defaults to None.
        throttle_period (Optional[float], optional): Throttle period in
            seconds. Defaults to None.
        **kwargs (Any): Additional keyword arguments to pass to the function.

    Yields:
        List[Any]: A list of results for each batch of inputs.

    Examples:
        >>> async def sample_func(x):
        >>>     return x * 2
        >>>
        >>> async for batch_results in bcall([1, 2, 3, 4, 5], sample_func, 2,
        >>>                                  retries=3, delay=1):
        >>>     print(batch_results)
    """
    input_ = to_list(input_)

    for i in range(0, len(input_), batch_size):
        batch = input_[i : i + batch_size]
        batch_results = await lcall(
            func,
            batch,
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
            max_concurrent=max_concurrent,
            throttle_period=throttle_period,
            **kwargs,
        )
        yield batch_results
