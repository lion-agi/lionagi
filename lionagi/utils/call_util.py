import asyncio
import functools
import logging
import time
from typing import Any, Callable, Generator, Iterable, List, Dict, Optional, Tuple

from aiocache import cached


def to_list(input: Any, flatten: bool = True, dropna: bool = False) -> List[Any]:
    """
    Convert input to a list, with options to flatten and drop None values.

    Args:
        input (Any): The input to convert.
        flatten (bool): If True, flattens the list if input is a list. Default is True.
        dropna (bool): If True, None values are removed from the list. Default is False.

    Returns:
        List[Any]: The input converted to a list.

    Examples:
        >>> to_list([1, [2, None], 3], flatten=True, dropna=True)
        [1, 2, 3]
        >>> to_list("hello", flatten=False)
        ["hello"]
    """
    if isinstance(input, list) and flatten:
        input = _flatten_list(input)
    elif isinstance(input, Iterable) and not isinstance(input, (str, dict)):
        try:
            input = list(input)
        except Exception as e:
            raise ValueError("Input cannot be converted to a list.") from e
    else:
        input = [input]
    if dropna:
        input = _dropna(input)
    return input

def lcall(
    input: Any, func: Callable, flatten: bool = False, 
    dropna: bool = False, **kwargs
) -> List[Any]:
    """
    Apply a function to each element of the input list, with options to flatten and drop None values.

    Args:
        input (Any): The input to process.
        func (Callable): The function to apply to each element.
        flatten (bool): If True, flattens the result. Default is False.
        dropna (bool): If True, None values are removed from the input. Default is False.
        **kwargs: Additional keyword arguments to pass to func.

    Returns:
        List[Any]: A list of results after applying the function.

    Examples:
        >>> lcall([1, 2, 3], lambda x: x * 2)
        [2, 4, 6]
        >>> lcall([1, 2, None], lambda x: x and x * 2, dropna=True)
        [2, 4]
    """
    lst = to_list(input=input, dropna=dropna)
    if len(to_list(func)) != 1:
        raise ValueError("There must be one and only one function for list calling.")
    if flatten:
        return to_list([func(i, **kwargs) for i in lst])
    return [func(i, **kwargs) for i in lst]

@functools.lru_cache(maxsize=None)
def is_coroutine_func(func: Callable) -> bool:
    """
    Check if the given function is a coroutine function.

    Args:
        func (Callable): The function to check.

    Returns:
        bool: True if the function is a coroutine function, False otherwise.

    Examples:
        >>> async def async_func(): pass
        >>> def sync_func(): pass
        >>> is_coroutine_func(async_func)
        True
        >>> is_coroutine_func(sync_func)
        False
    """
    return asyncio.iscoroutinefunction(func)

async def alcall(
    input: Any, func: Callable, flatten: bool = False, **kwargs
)-> List[Any]:
    """
    Asynchronously apply a function to each element in the input.

    Args:
        input (Any): The input to process.
        func (Callable): The function to apply.
        flatten (bool, optional): Whether to flatten the result. Default is False.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results after asynchronously applying the function.

    Examples:
        >>> async def square(x): return x * x
        >>> asyncio.run(alcall([1, 2, 3], square))
        [1, 4, 9]
    """
    lst = to_list(input=input)
    tasks = [func(i, **kwargs) for i in lst]
    outs = await asyncio.gather(*tasks)
    return to_list(outs, flatten=flatten)

async def mcall(
    input: Any, func: Any, explode: bool = False, **kwargs
) -> List[Any]:
    """
    Asynchronously map a function or functions over an input or inputs.

    Args:
        input (Any): The input or inputs to process.
        func (Any): The function or functions to apply.
        explode (bool, optional): Whether to apply each function to each input. Default is False.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results after applying the function(s).

    Examples:
        >>> async def add_one(x): return x + 1
        >>> asyncio.run(mcall([1, 2, 3], add_one))
        [2, 3, 4]
        
    """
    input_ = to_list(input, dropna=True)
    funcs_ = to_list(func, dropna=True)
    
    if explode:
        tasks = [
            _alcall(input_, f, flatten=True, **kwargs)
            for f in funcs_
        ]
        return await asyncio.gather(*tasks)
    else:
        if len(input_) != len(funcs_):
            raise ValueError("Inputs and functions must be the same length for map calling.")
        tasks = [
            _call_handler(func, inp, **kwargs) 
            for inp, func in zip(input, func)
        ]
        return await asyncio.gather(*tasks)

async def bcall(input: Any, func: Callable, batch_size: int, **kwargs) -> List[Any]:
    """
    Asynchronously call a function on batches of inputs.

    Args:
        input (Any): The input to process.
        func (Callable): The function to apply.
        batch_size (int): The size of each batch.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results after applying the function in batches.

    Examples:
        >>> async def sum_batch(batch): return sum(batch)
        >>> asyncio.run(bcall([1, 2, 3, 4], sum_batch, batch_size=2))
        [3, 7]
    """
    results = []
    input = to_list(input)
    for i in range(0, len(input), batch_size):
        batch = input[i:i + batch_size]
        batch_results = await alcall(batch, func, **kwargs)
        results.extend(batch_results)

    return results

async def tcall(
    func: Callable, *args, delay: float = 0, err_msg: Optional[str] = None, 
    ignore_err: bool = False, timing: bool = False, 
    timeout: Optional[float] = None, **kwargs
) -> Any:
    """
    Asynchronously call a function with optional delay, timeout, and error handling.

    Args:
        func (Callable): The function to call.
        *args: Positional arguments to pass to the function.
        delay (float): Delay before calling the function, in seconds.
        err_msg (Optional[str]): Custom error message.
        ignore_err (bool): If True, ignore errors and return default.
        timing (bool): If True, return a tuple (result, duration).
        default (Any): Default value to return on error.
        timeout (Optional[float]): Timeout for the function call, in seconds.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, or (result, duration) if timing is True.

    Examples:
        >>> async def example_func(x): return x
        >>> asyncio.run(tcall(example_func, 5, timing=True))
        (5, duration)
    """
    async def async_call() -> Tuple[Any, float]:
        start_time = time.time()
        if timeout is not None:
            result = await asyncio.wait_for(func(*args, **kwargs), timeout)
        try:
            await asyncio.sleep(delay)
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

    if asyncio.iscoroutinefunction(func):
        return await async_call()
    else: 
        return sync_call()
       
async def rcall(
    func: Callable, *args, retries: int = 0, delay: float = 1.0, 
    backoff_factor: float = 2.0, default: Any = None, 
    timeout: Optional[float] = None, **kwargs
) -> Any:
    """
    Asynchronously retry a function call with exponential backoff.

    Args:
        func (Callable): The function to call.
        *args: Positional arguments to pass to the function.
        retries (int): Number of retry attempts.
        delay (float): Initial delay between retries, in seconds.
        backoff_factor (float): Factor by which to multiply delay for each retry.
        default (Any): Default value to return if all retries fail.
        timeout (Optional[float]): Timeout for each function call, in seconds.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, or default if retries are exhausted.

    Examples:
        >>> async def example_func(x): return x
        >>> asyncio.run(rcall(example_func, 5, retries=2))
        5
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
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                break
    if result is None and default is not None:
        return default
    elif last_exception is not None:
        raise last_exception
    else:
        raise RuntimeError("rcall failed without catching an exception")

class CallDecorator:

    """
    Call Decorators
    """


    @staticmethod
    def timeout(timeout: int) -> Callable:
        """
        Decorator to apply a timeout to an asynchronous function.

        Args:
            timeout (int): Timeout duration in seconds.

        Returns:
            Callable: A decorated function with applied timeout.

        Examples:
            >>> @CallDecorator.timeout(5)
            ... async def long_running_task(): pass
            ... # The task will timeout after 5 seconds
        """
        def decorator(func: Callable[..., Any]) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await rcall(func, *args, timeout=timeout, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def retry(
        retries: int = 3, delay: float = 2.0, backoff_factor: float = 2.0
    ) -> Callable:
        """
        Decorator to retry an asynchronous function with exponential backoff.

        Args:
            retries (int): Number of retry attempts.
            initial_delay (float): Initial delay between retries in seconds.
            backoff_factor (float): Factor by which to multiply delay for each retry.

        Returns:
            Callable: A decorated function with applied retry logic.

        Examples:
            >>> @CallDecorator.retry(retries=2, initial_delay=1.0, backoff_factor=2.0)
            ... async def fetch_data(): pass
            ... # This function will retry up to 2 times with increasing delays
        """
        def decorator(func: Callable[..., Any]) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await rcall(
                    func, *args, retries=retries, delay=delay, 
                    backoff_factor=backoff_factor, **kwargs
                )
            return wrapper
        return decorator

    @staticmethod
    def default(default_value: Any) -> Callable:
        def decorator(func: Callable[..., Any]) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await rcall(func, *args, default=default_value, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def throttle(period: int) -> Callable:
        """
        A static method to create a throttling decorator using the Throttle class.

        Args:
            period (int): The minimum time period (in seconds) between successive calls.

        Returns:
            Callable: A decorator that applies a throttling mechanism to the decorated 
            function.
        """
        return Throttle(period)

    @staticmethod
    def map(function: Callable[[Any], Any]) -> Callable:
        """
        Decorator that applies a mapping function to the results of an asynchronous 
        function.

        This decorator transforms each element in the list returned by the decorated 
        function using the provided mapping function.

        Args:
            function (Callable[[Any], Any]): A function to apply to each element of the list.

        Returns:
            Callable: A decorated function that maps the provided function over its results.

        Examples:
            >>> @CallDecorator.map(lambda x: x * 2)
            ... async def get_numbers(): return [1, 2, 3]
            >>> asyncio.run(get_numbers())
            [2, 4, 6]
        """
        def decorator(func: Callable[..., List[Any]]) -> Callable:
            if is_coroutine_func(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs) -> List[Any]:
                    values = await func(*args, **kwargs)
                    return [function(value) for value in values]
                return async_wrapper
            else:    
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs) -> List[Any]:
                    values = func(*args, **kwargs)
                    return [function(value) for value in values]
                return sync_wrapper
        return decorator

    @staticmethod
    def compose(*functions: Callable[[Any], Any]) -> Callable:
        """
        Decorator factory that composes multiple functions. The output of each 
        function is passed as the input to the next, in the order they are provided.

        Args:
            *functions: Variable length list of functions to compose.

        Returns:
            Callable: A new function that is the composition of the given functions.
        """
        def decorator(func: Callable) -> Callable:
            if not any(is_coroutine_func(f) for f in functions):
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    value = func(*args, **kwargs)
                    for function in functions:
                        try:
                            value = function(value)
                        except Exception as e:
                            raise ValueError(f"Error in function {function.__name__}: {e}")
                    return value
                return sync_wrapper
            elif all(is_coroutine_func(f) for f in functions):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    value = func(*args, **kwargs)
                    for function in functions:
                        try:
                            value = await function(value)
                        except Exception as e:
                            raise ValueError(f"Error in function {function.__name__}: {e}")
                    return value
                return async_wrapper        
            else:
                raise ValueError("Cannot compose both synchronous and asynchronous functions.")
        return decorator

    @staticmethod
    def pre_post_process(
        preprocess: Callable[..., Any], postprocess: Callable[..., Any]
    ) -> Callable:
        """
        Decorator that applies preprocessing and postprocessing functions to the arguments 
        and result of an asynchronous function.

        Args:
            preprocess (Callable[..., Any]): A function to preprocess each argument.
            postprocess (Callable[..., Any]): A function to postprocess the result.

        Returns:
            Callable: A decorated function with preprocessing and postprocessing applied.

        Examples:
            >>> @CallDecorator.pre_post_process(lambda x: x * 2, lambda x: x + 1)
            ... async def compute(x): return x
            >>> asyncio.run(compute(5))
            21  # (5 * 2) -> 10, compute(10) -> 10, 10 + 1 -> 21
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if is_coroutine_func(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs) -> Any:
                    preprocessed_args = [preprocess(arg) for arg in args]
                    preprocessed_kwargs = {k: preprocess(v) for k, v in kwargs.items()}
                    result = await func(*preprocessed_args, **preprocessed_kwargs)
                    return postprocess(result)
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs) -> Any:
                    preprocessed_args = [preprocess(arg) for arg in args]
                    preprocessed_kwargs = {k: preprocess(v) for k, v in kwargs.items()}
                    result = func(*preprocessed_args, **preprocessed_kwargs)
                    return postprocess(result)
                return sync_wrapper
            
        return decorator

    @staticmethod
    def cache(func: Callable, ttl=600, maxsize=None) -> Callable:
        """
        Decorator that caches the results of function calls (both sync and async). 
        If the function is called again with the same arguments, 
        the cached result is returned instead of re-executing the function.

        Args:
            func (Callable): The function (can be sync or async) whose results need to be cached.

        Returns:
            Callable: A decorated function with caching applied.
        """

        if is_coroutine_func(func):
            # Asynchronous function handling
            @cached(ttl=ttl)
            async def cached_async(*args, **kwargs) -> Any:
                return await func(*args, **kwargs)
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                return await cached_async(*args, **kwargs)

            return async_wrapper

        else:
            # Synchronous function handling
            @functools.lru_cache(maxsize=maxsize)
            def cached_sync(*args, **kwargs) -> Any:
                return func(*args, **kwargs)
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                return cached_sync(*args, **kwargs)

            return sync_wrapper

    @staticmethod
    def filter(predicate: Callable[[Any], bool]) -> Callable:
        """
        Decorator that filters the results of an asynchronous function based on a predicate 
        function.

        Args:
            predicate (Callable[[Any], bool]): A function that returns True for items to keep.

        Returns:
            Callable: A decorated function that filters its results based on the predicate.

        Examples:
            >>> @CallDecorator.filter(lambda x: x % 2 == 0)
            ... async def get_numbers(): return [1, 2, 3, 4, 5]
            >>> asyncio.run(get_numbers())
            [2, 4]
        """
        def decorator(func: Callable[..., List[Any]]) -> Callable:
            if is_coroutine_func(func):
                @functools.wraps(func)
                async def wrapper(*args, **kwargs) -> List[Any]:
                    values = await func(*args, **kwargs)
                    return [value for value in values if predicate(value)]
                return wrapper
            else:
                @functools.wraps(func)
                def wrapper(*args, **kwargs) -> List[Any]:
                    values = func(*args, **kwargs)
                    return [value for value in values if predicate(value)]
                return wrapper
        return decorator

    @staticmethod
    def reduce(function: Callable[[Any, Any], Any], initial: Any) -> Callable:
        """
        Decorator that reduces the results of an asynchronous function to a single value using 
        the specified reduction function.

        Args:
            function (Callable[[Any, Any], Any]): A reduction function to apply.
            initial (Any): The initial value for the reduction.

        Returns:
            Callable: A decorated function that reduces its results to a single value.

        Examples:
            >>> @CallDecorator.reduce(lambda x, y: x + y, 0)
            ... async def get_numbers(): return [1, 2, 3, 4]
            >>> asyncio.run(get_numbers())
            10  # Sum of the numbers
        """
        def decorator(func: Callable[..., List[Any]]) -> Callable:
            if is_coroutine_func(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs) -> Any:
                    values = await func(*args, **kwargs)
                    return functools.reduce(function, values, initial)
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs) -> Any:
                    values = func(*args, **kwargs)
                    return functools.reduce(function, values, initial)
                return sync_wrapper
        return decorator

    @staticmethod
    def max_concurrency(limit: int = 5) -> Callable:
        """
        Decorator to limit the maximum number of concurrent executions of an async function.

        Args:
            limit (int): The maximum number of concurrent tasks allowed.

        Returns:
            Callable: A decorated function with limited concurrency.

        Examples:
            >>> @CallDecorator.max_concurrency(3)
            ... async def process_data(): pass
        """
        def decorator(func: Callable) -> Callable:
            if not asyncio.iscoroutinefunction(func):
                raise TypeError("max_concurrency decorator can only be used with async functions.")
            semaphore = asyncio.Semaphore(limit)

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                async with semaphore:
                    return await func(*args, **kwargs)

            return wrapper
        
        return decorator

    @staticmethod
    def throttle(period: int) -> Callable:
        """
        A static method to create a throttling decorator. This method utilizes the Throttle 
        class to enforce a minimum time period between successive calls of the decorated function.

        Args:
            period (int): The minimum time period, in seconds, that must elapse between successive 
            calls to the decorated function.

        Returns:
            Callable: A decorator that applies a throttling mechanism to the decorated function, 
            ensuring that the function is not called more frequently than the specified period.

        Examples:
            >>> @CallDecorator.throttle(2)  # Ensures at least 2 seconds between calls
            ... async def fetch_data(): pass

            This decorator is particularly useful in scenarios like rate-limiting API calls or 
            reducing the frequency of resource-intensive operations.
        """
        return Throttle(period)

class Throttle:
    """
    A class that provides a throttling mechanism for function calls.

    When used as a decorator, it ensures that the decorated function can only be called
    once per specified period. Subsequent calls within this period are delayed to enforce
    this constraint.

    Attributes:
        period (int): The minimum time period (in seconds) between successive calls.

    Methods:
        __call__: Decorates a synchronous function with throttling.
        __call_async__: Decorates an asynchronous function with throttling.
    """

    def __init__(self, period: int) -> None:
        """
        Initializes a new instance of Throttle.

        Args:
            period (int): The minimum time period (in seconds) between successive calls.
        """
        self.period = period
        self.last_called = 0

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorates a synchronous function with the throttling mechanism.

        Args:
            func (Callable[..., Any]): The synchronous function to be throttled.

        Returns:
            Callable[..., Any]: The throttled synchronous function.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - self.last_called
            if elapsed < self.period:
                time.sleep(self.period - elapsed)
            self.last_called = time.time()
            return func(*args, **kwargs)

        return wrapper

    async def __call_async__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorates an asynchronous function with the throttling mechanism.

        Args:
            func (Callable[..., Any]): The asynchronous function to be throttled.

        Returns:
            Callable[..., Any]: The throttled asynchronous function.
        """
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - self.last_called
            if elapsed < self.period:
                await asyncio.sleep(self.period - elapsed)
            self.last_called = time.time()
            return await func(*args, **kwargs)

        return wrapper
    
def _dropna(l: List[Any]) -> List[Any]:
    """
    Remove None values from a list.

    Args:
        l (List[Any]): A list potentially containing None values.

    Returns:
        List[Any]: A list with None values removed.

    Examples:
        >>> _dropna([1, None, 3, None])
        [1, 3]
    """
    return [item for item in l if item is not None]
    
def _flatten_list(l: List[Any], dropna: bool = True) -> List[Any]:
    """
    Flatten a nested list, optionally removing None values.

    Args:
        l (List[Any]): A nested list to flatten.
        dropna (bool): If True, None values are removed. Default is True.

    Returns:
        List[Any]: A flattened list.

    Examples:
        >>> _flatten_list([[1, 2], [3, None]], dropna=True)
        [1, 2, 3]
        >>> _flatten_list([[1, [2, None]], 3], dropna=False)
        [1, 2, None, 3]
    """
    flattened_list = list(_flatten_list_generator(l, dropna))
    return _dropna(flattened_list) if dropna else flattened_list

def _flatten_list_generator(
    l: List[Any], dropna: bool = True
) -> Generator[Any, None, None]:
    """
    Generator for flattening a nested list.

    Args:
        l (List[Any]): A nested list to flatten.
        dropna (bool): If True, None values are omitted. Default is True.

    Yields:
        Generator[Any, None, None]: A generator yielding flattened elements.

    Examples:
        >>> list(_flatten_list_generator([[1, [2, None]], 3], dropna=False))
        [1, 2, None, 3]
    """
    for i in l:
        if isinstance(i, list):
            yield from _flatten_list_generator(i, dropna)
        else:
            yield i


def _custom_error_handler(error: Exception, error_map: Dict[type, Callable]) -> None:
    """
    Handle errors based on a given error mapping.

    Args:
        error (Exception): The error to handle.
        error_map (Dict[type, Callable]): A dictionary mapping error types to handler functions.

    Examples:
        >>> def handle_value_error(e): print("ValueError occurred")
        >>> custom_error_handler(ValueError(), {ValueError: handle_value_error})
        ValueError occurred
    """
    handler = error_map.get(type(error))
    if handler:
        handler(error)
    else:
        logging.error(f"Unhandled error: {error}")

async def _call_handler(
    func: Callable, *args, error_map: Dict[type, Callable] = None, 
    **kwargs
) -> Any:
    """
    Call a function with error handling, supporting both synchronous and asynchronous functions.

    Args:
        func (Callable): The function to call.
        *args: Positional arguments to pass to the function.
        error_map (Dict[type, Callable], optional): A dictionary mapping error types to handler functions.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call.

    Raises:
        Exception: Propagates any exceptions not handled by the error_map.

    Examples:
        >>> async def async_add(x, y): return x + y
        >>> asyncio.run(call_handler(async_add, 1, 2))
        3
    """
    try:
        if is_coroutine_func(func):
            # Checking for a running event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:  # No running event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # Running the coroutine in the new loop
                result = loop.run_until_complete(func(*args, **kwargs))
                loop.close()
                return result

            if loop.is_running():
                return asyncio.ensure_future(func(*args, **kwargs))
            else:
                return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    except Exception as e:
        if error_map:
            _custom_error_handler(e, error_map)
        else:
            logging.error(f"Error in call_handler: {e}")
        raise


async def _alcall(
    input: Any, func: Callable, flatten: bool = False, **kwargs
)-> List[Any]:
    """
    Asynchronously apply a function to each element in the input.

    Args:
        input (Any): The input to process.
        func (Callable): The function to apply.
        flatten (bool, optional): Whether to flatten the result. Default is False.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results after asynchronously applying the function.

    Examples:
        >>> async def square(x): return x * x
        >>> asyncio.run(alcall([1, 2, 3], square))
        [1, 4, 9]
    """
    lst = to_list(input=input)
    tasks = [_call_handler(func, i, **kwargs) for i in lst]
    outs = await asyncio.gather(*tasks)
    return to_list(outs, flatten=flatten)

        
async def _tcall(
    func: Callable, *args, delay: float = 0, err_msg: Optional[str] = None, 
    ignore_err: bool = False, timing: bool = False, 
    default: Any = None, timeout: Optional[float] = None, **kwargs
) -> Any:
    """
    Asynchronously call a function with optional delay, timeout, and error handling.

    Args:
        func (Callable): The function to call.
        *args: Positional arguments to pass to the function.
        delay (float): Delay before calling the function, in seconds.
        err_msg (Optional[str]): Custom error message.
        ignore_err (bool): If True, ignore errors and return default.
        timing (bool): If True, return a tuple (result, duration).
        default (Any): Default value to return on error.
        timeout (Optional[float]): Timeout for the function call, in seconds.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, or (result, duration) if timing is True.

    Examples:
        >>> async def example_func(x): return x
        >>> asyncio.run(tcall(example_func, 5, timing=True))
        (5, duration)
    """
    start_time = time.time()
    try:
        await asyncio.sleep(delay)
        # Apply timeout to the function call
        if timeout is not None:
            result = await asyncio.wait_for(func(*args, **kwargs), timeout)
        else:
            if is_coroutine_func(func):
                return await func( *args, **kwargs)
            return func(*args, **kwargs)
        duration = time.time() - start_time
        return (result, duration) if timing else result
    except asyncio.TimeoutError as e:
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
        