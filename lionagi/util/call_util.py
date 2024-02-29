from __future__ import annotations
import time

from typing import Any, Callable, List, Tuple
from lionagi.util.convert_util import to_list
from lionagi.util.async_util import AsyncUtil


def lcall(
    input_: Any, func: Callable, flatten: bool = False, dropna: bool = False, **kwargs
) -> List[Any]:
    """
    applies a function to each element of the input list, with options to flatten
    results and drop None values.

    this function facilitates the batch application of a transformation or operation
    to each item in an input list. it is versatile, supporting both flattening of the
    result list and removal of None values from the output, making it suitable for a
    wide range of data manipulation tasks. additional arguments to the applied
    function can be passed dynamically, allowing for flexible function application.

    Args:
        input_ (Any):
            The input list or iterable to process. each element will be passed to the
            provided `func` callable.
        func (Callable):
            The function to apply to each element of `input_`. this function can be any
            callable that accepts the elements of `input_` as arguments.
        flatten (bool, optional):
            If True, the resulting list is flattened. useful when `func` returns a list.
            defaults to False.
        dropna (bool, optional):
            If True, None values are removed from the final list. defaults to False.
        **kwargs:
            Additional keyword arguments to be passed to `func`.

    Returns:
        List[Any]:
            The list of results after applying `func` to each input element, modified
            according to `flatten` and `dropna` options.

    Examples:
        Apply a doubling function to each element:
        >>> lcall([1, 2, 3], lambda x: x * 2)
        [2, 4, 6]

        apply a function that returns lists, then flatten the result:
        >>> lcall([1, 2, None], lambda x: [x, x] if x else x, flatten=True, dropna=True)
        [1, 1, 2, 2]
    """
    lst = to_list(input_=input_, dropna=dropna)
    if len(to_list(func)) != 1:
        raise ValueError("There must be one and only one function for list calling.")

    return to_list([func(i, **kwargs) for i in lst], flatten=flatten, dropna=dropna)


async def alcall(
    input_: Any = None, func: Callable = None, flatten: bool = False, **kwargs
) -> List[Any]:
    # noinspection GrazieInspection
    """
    asynchronously applies a function to each element in the input.

    this async function is designed for operations where a given async function needs to
    be applied to each element of an input list concurrently. it allows for the results
    to be flattened and provides the flexibility to pass additional keyword arguments to
    the function being applied. this is especially useful in scenarios where processing
    each element of the input can be performed independently and concurrently, improving
    efficiency and overall execution time.

    Args:
        input_ (Any, optional):
            The input to process. defaults to None, which requires `func` to be capable of
            handling the absence of explicit input.
        func (Callable, optional):
            The asynchronous function to apply. defaults to None.
        flatten (bool, optional):
            Whether to flatten the result. useful when `func` returns a list or iterable
            that should be merged into a single list. defaults to False.
        **kwargs:
            Keyword arguments to pass to the function.

    Returns:
        List[Any]:
            A list of results after asynchronously applying the function to each element
            of the input, potentially flattened.

    examples:
        >>> async def square(x): return x * x
        >>> await alcall([1, 2, 3], square)
        [1, 4, 9]
    """
    if input_:
        lst = to_list(input_=input_)
        tasks = [func(i, **kwargs) for i in lst]
    else:
        tasks = [func(**kwargs)]

    outs = await AsyncUtil.execute_tasks(*tasks)
    return to_list(outs, flatten=flatten)


async def mcall(input_: Any, func: Any, explode: bool = False, **kwargs) -> tuple[Any]:
    """
    asynchronously map a function or functions over an input_ or inputs.

    Args:
        input_ (Any):
            The input_ or inputs to process.
        func (Any):
            The function or functions to apply.
        explode (bool, optional):
            Whether to apply each function to each input_. default is False.
        **kwargs:
            Keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results after applying the function(s).

    examples:
        >>> async def add_one(x):
        >>>     return x + 1
        >>> asyncio.run(mcall([1, 2, 3], add_one))
        [2, 3, 4]

    """
    input_ = to_list(input_, dropna=True)
    funcs_ = to_list(func, dropna=True)

    if explode:
        tasks = [_alcall(input_, f, flatten=True, **kwargs) for f in funcs_]
        return await AsyncUtil.execute_tasks(*tasks)
    else:
        if len(input_) != len(funcs_):
            raise ValueError(
                "Inputs and functions must be the same length for map calling."
            )
        tasks = [AsyncUtil.handle_async_sync(func, inp, **kwargs) for inp, func in zip(input_, func)]
        return await AsyncUtil.execute_tasks(*tasks)


async def bcall(input_: Any, func: Callable, batch_size: int, **kwargs) -> List[Any]:
    """
    asynchronously call a function on batches of inputs.

    Args:
        input_ (Any): The input_ to process.
        func (Callable): The function to apply.
        batch_size (int): The size of each batch.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results after applying the function in batches.

    examples:
        >>> async def sum_batch(batch_): return sum(batch_)
        >>> asyncio.run(bcall([1, 2, 3, 4], sum_batch, batch_size=2))
        [3, 7]
    """
    results = []
    input_ = to_list(input_)
    for i in range(0, len(input_), batch_size):
        batch = input_[i : i + batch_size]
        batch_results = await alcall(batch, func, **kwargs)
        results.extend(batch_results)

    return results


async def tcall(
    func: Callable,
    *args,
    delay: float = 0,
    err_msg: str | None = None,
    ignore_err: bool = False,
    timing: bool = False,
    timeout: float | None = None,
    **kwargs,
) -> Any:
    """
    asynchronously executes a function with an optional delay, error handling, and timing.

    this utility allows for the asynchronous invocation of a callable with added controls
    for execution delay, customizable timeout, and optional error suppression. it can
    also measure the execution time if required. this function is useful in scenarios
    where operations need to be scheduled with a delay, executed within a certain time
    frame, or when monitoring execution duration.

    Args:
        func (Callable):
            The asynchronous function to be called.
        *args:
            Positional arguments to pass to the function.
        delay (float, optional):
            Time in seconds to wait before executing the function. default to 0.
        err_msg (str | None, optional):
            Custom error message to display if an error occurs. defaults to None.
        ignore_err (bool, optional):
            If True, suppresses any errors that occur during function execution,
            optionally returning a default value. defaults to False.
        timing (bool, optional):
            If True, returns a tuple containing the result of the function and the
            execution duration in seconds. defaults to False.
        timeout (float | None, optional):
            Maximum time in seconds allowed for the function execution. if the execution
            exceeds this time, a timeout error is raised. defaults to None.
        **kwargs:
            Keyword arguments to pass to the function.

    Returns:
        Any:
            The result of the function call. if `timing` is True, returns a tuple of
            (result, execution duration).

    examples:
        >>> async def sample_function(x):
        ...     return x * x
        >>> await tcall(sample_function, 3, delay=1, timing=True)
        (9, execution_duration)
    """

    async def async_call() -> Tuple[Any, float]:
        start_time = time.time()
        if timeout is not None:
            result = await AsyncUtil.execute_timeout(func(*args, **kwargs), timeout)
            duration = time.time() - start_time
            return (result, duration) if timing else result
        try:
            await AsyncUtil.sleep(delay)
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            return (result, duration) if timing else result
        except Exception as e:
            handle_error(e)

    def sync_call() -> Tuple[Any, float]:
        start_time = time.time()
        try:
            time.sleep(delay)
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            return (result, duration) if timing else result
        except Exception as e:
            handle_error(e)

    def handle_error(e: Exception):
        _msg = f"{err_msg} Error: {e}" if err_msg else f"An error occurred: {e}"
        print(_msg)
        if not ignore_err:
            raise

    if AsyncUtil.is_coroutine_func(func):
        return await async_call()
    else:
        return sync_call()


async def rcall(
    func: Callable,
    *args,
    retries: int = 0,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    default: Any = None,
    timeout: float | None = None,
    **kwargs,
) -> Any:
    """
    asynchronously retries a function call with exponential backoff.

    designed for resilience, this function attempts to call an asynchronous function
    multiple times with increasing delays between attempts. this is particularly
    beneficial for operations that may fail due to transient issues. the function
    supports specifying a timeout for each attempt, a default return value in case of
    persistent failures, and a backoff factor to control the delay increase.

    Args:
        func (Callable):
            The asynchronous function to retry.
        *args:
            Positional arguments for the function.
        retries (int, optional):
            The number of retry attempts before giving up. default to 0.
        delay (float, optional):
            Initial delay between retries in seconds. default to 1.0.
        backoff_factor (float, optional):
            Multiplier for the delay between retries, for exponential backoff.
            default to 2.0.
        default (Any, optional):
            A value to return if all retries fail. defaults to None.
        timeout (float | None, optional):
            Maximum duration in seconds for each attempt. defaults to None.
        **kwargs:
            Keyword arguments for the function.

    Returns:
        Any:
            The result of the function call if successful within the retry attempts,
            otherwise the `default` value if specified.

    examples:
        >>> async def fetch_data():
        ...     # Simulate a fetch operation that might fail
        ...     raise Exception("temporary error")
        >>> await rcall(fetch_data, retries=3, delay=2, default="default value")
        'default value'
    """
    last_exception = None
    result = None

    for attempt in range(retries + 1) if retries == 0 else range(retries):
        try:
            # Using tcall for each retry attempt with timeout and delay
            result = await _tcall(func, *args, timeout=timeout, **kwargs)
            return result
        except Exception as e:
            last_exception = e
            if attempt < retries:
                await AsyncUtil.sleep(delay)
                delay *= backoff_factor
            else:
                break
    if result is None and default is not None:
        return default
    elif last_exception is not None:
        raise last_exception
    else:
        raise RuntimeError("rcall failed without catching an exception")


def _dropna(lst_: List[Any]) -> List[Any]:
    """
    Remove None values from a list.

    Args:
        lst_ (List[Any]): A list potentially containing None values.

    Returns:
        List[Any]: A list with None values removed.

    Examples:
        >>> _dropna([1, None, 3, None])
        [1, 3]
    """
    return [item for item in lst_ if item is not None]

async def _alcall(
    input_: Any, func: Callable, flatten: bool = False, **kwargs
) -> List[Any]:
    """
    asynchronously apply a function to each element in the input_.

    Args:
        input (Any): The input_ to process.
        func (Callable): The function to apply.
        flatten (bool, optional): Whether to flatten the result. default is False.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results after asynchronously applying the function.

    examples:
        >>> async def square(x): return x * x
        >>> asyncio.run(alcall([1, 2, 3], square))
        [1, 4, 9]
    """
    lst = to_list(input_=input_)
    tasks = [AsyncUtil.handle_async_sync(func, i, **kwargs) for i in lst]
    outs = await AsyncUtil.execute_tasks(*tasks)
    return to_list(outs, flatten=flatten)


async def _tcall(
    func: Callable,
    *args,
    delay: float = 0,
    err_msg: str | None = None,
    ignore_err: bool = False,
    timing: bool = False,
    default: Any = None,
    timeout: float | None = None,
    **kwargs,
) -> Any:
    """
    asynchronously call a function with optional delay, timeout, and error handling.

    Args:
        func (Callable): The function to call.
        *args: Positional arguments to pass to the function.
        delay (float): Delay before calling the function, in seconds.
        err_msg (str | None): Custom error message.
        ignore_err (bool): If True, ignore errors and return default.
        timing (bool): If True, return a tuple (result, duration).
        default (Any): Default value to return on error.
        timeout (float | None): Timeout for the function call, in seconds.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, or (result, duration) if timing is True.

    examples:
        >>> async def example_func(x): return x
        >>> asyncio.run(tcall(example_func, 5, timing=True))
        (5, duration)
    """
    start_time = time.time()
    try:
        await AsyncUtil.sleep(delay)
        # Apply timeout to the function call
        if timeout is not None:
            result = await AsyncUtil.execute_timeout(func(*args, **kwargs), timeout)
        else:
            if AsyncUtil.is_coroutine_func(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        duration = time.time() - start_time
        return (result, duration) if timing else result
    except AsyncUtil.TimeoutError as e:
        err_msg = f"{err_msg} Error: {e}" if err_msg else f"An error occurred: {e}"
        print(err_msg)
        if ignore_err:
            return (default, time.time() - start_time) if timing else default
        else:
            raise e  # Re-raise the timeout exception
    except Exception as e:
        err_msg = f"{err_msg} Error: {e}" if err_msg else f"An error occurred: {e}"
        print(err_msg)
        if ignore_err:
            return (default, time.time() - start_time) if timing else default
        else:
            raise e
