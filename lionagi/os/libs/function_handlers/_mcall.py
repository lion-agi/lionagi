"""
This module provides a mapping call mechanism to apply functions over inputs
asynchronously with options such as retries, initial delay, backoff factor,
timeout, error handling, and throttling.

Functions:
- mcall: Apply functions over inputs asynchronously with customizable options.
"""

import asyncio
from typing import Any, List, Union, Dict, Callable
from lionagi.os.libs.data_handlers import to_list
from lionagi.os.libs.function_handlers._lcall import lcall
from lionagi.os.libs.function_handlers._rcall import rcall


async def mcall(
    input_: Any,
    /,
    func: Any,
    *,
    explode: bool = False,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = ...,
    timeout: Union[float, None] = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: Union[str, None] = None,
    error_map: Union[Dict[type, Callable], None] = None,
    max_concurrent: Union[int, None] = None,
    throttle_period: Union[float, None] = None,
    flatten: bool = False,
    dropna: bool = False,
    **kwargs: Any,
) -> List[Any]:
    """
    Apply functions over inputs asynchronously with customizable options.

    This function allows executing multiple functions over multiple inputs in
    parallel with support for retries, initial delay, backoff factor, timeout,
    error handling, concurrency control, and throttling.

    Args:
        input_ (Any): The input data to be processed.
        func (Any): The function or list of functions to be applied.
        explode (bool, optional): Whether to explode the function calls,
            applying each function to all inputs. Defaults to False.
        retries (int, optional): Number of retry attempts for each function.
            Defaults to 0.
        initial_delay (float, optional): Initial delay before starting the
            execution. Defaults to 0.
        delay (float, optional): Delay between retry attempts. Defaults to 0.
        backoff_factor (float, optional): Factor by which the delay increases
            after each attempt. Defaults to 1.
        default (Any, optional): Default value to return if all attempts fail.
            Defaults to ... (ellipsis).
        timeout (Union[float, None], optional): Timeout for each function
            execution. Defaults to None.
        timing (bool, optional): Whether to return the execution duration.
            Defaults to False.
        verbose (bool, optional): Whether to print retry messages. Defaults to
            True.
        error_msg (Union[str, None], optional): Custom error message. Defaults
            to None.
        error_map (Union[Dict[type, Callable], None], optional): A dictionary
            mapping exception types to error handling functions. Defaults to
            None.
        max_concurrent (Union[int, None], optional): Maximum number of
            concurrent executions. Defaults to None.
        throttle_period (Union[float, None], optional): Minimum time period
            between successive function executions. Defaults to None.
        flatten (bool, optional): Whether to flatten the output list. Defaults
            to False.
        dropna (bool, optional): Whether to drop None values from the output
            list. Defaults to False.
        **kwargs (Any): Additional keyword arguments to pass to each function.

    Returns:
        List[Any]: The results of the function calls, optionally including the
            duration of execution if `timing` is True.

    Raises:
        ValueError: If the length of inputs and functions do not match when not
            exploding the function calls.
    """
    input_ = to_list(input_)
    func = to_list(func)

    if explode:
        tasks = [
            lcall(
                f,
                input_,
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
                flatten=flatten,
                dropna=dropna,
                **kwargs,
            )
            for f in func
        ]
        return await asyncio.gather(*tasks)
    elif len(func) == 1:
        tasks = [
            rcall(
                func[0],
                inp,
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
            for inp in input_
        ]
        return await asyncio.gather(*tasks)

    elif len(input_) == len(func):
        tasks = [
            rcall(
                f,
                inp,
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
            for inp, f in zip(input_, func)
        ]
        return await asyncio.gather(*tasks)
    else:
        raise ValueError(
            "Inputs and functions must be the same length for map calling."
        )
