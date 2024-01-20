from collections import OrderedDict
import asyncio
import functools as ft
from aiocache import cached
import concurrent.futures
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from .sys_util import create_copy
from .nested_util import to_list


def lcall(
    input_: Any, func_: Callable, flatten: bool = False, 
    dropna: bool = False, **kwargs) -> List[Any]:
    """
    list call: Applies a function to each element in a list, with options for flattening and dropping NAs.

    Args:
        input_ (Any): The input, potentially a list, to process.
        func_ (Callable): The function to be applied to each element.
        flatten (bool, optional): If True, flattens the input.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list containing the results of the function call on each element.

    Raises:
        ValueError: If the function cannot be applied to an element in the list.

    Examples:
        >>> lcall([1, 2, 3], lambda x: x + 1)
        [2, 3, 4]
        >>> lcall([1, None, 3], lambda x: x + 1, dropna=True)
        [2, 4]
    """
    try:
        lst = to_list(input_=input_, flatten=flatten, dropna=dropna)
        return [func_(i, **kwargs) for i in lst]
    except Exception as e:
        raise ValueError(f"Function {func_.__name__} cannot be applied: {e}")

async def alcall(
    input_: Any, func_: Callable, flatten: bool = False, 
    dropna: bool = False, **kwargs) -> List[Any]:
    """
    Async list call: Asynchronously applies a function to each element in a list, with options for flattening and dropping NAs.

    Args:
        input_ (Any): The input, potentially a list, to process.
        func_ (Callable): The function (can be async or sync) to be applied to each element.
        flatten (bool, optional): If True, flattens the input.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list containing the results of the function call on each element.

    Raises:
        ValueError: If the function cannot be applied to an element in the list.

    Examples:
        >>> async def add_one(x): return x + 1
        >>> asyncio.run(alcall([1, 2, 3], add_one))
        [2, 3, 4]
        >>> asyncio.run(alcall([1, None, 3], add_one, dropna=True))
        [2, 4]
    """
    try:
        lst = to_list(input_=input_, flatten=flatten, dropna=dropna)
        if asyncio.iscoroutinefunction(func_):
            tasks = [func_(i, **kwargs) for i in lst]
            return await asyncio.gather(*tasks)
        else:
            return lcall(input_, func_, flatten=flatten, dropna=dropna, **kwargs)
    except Exception as e:
        raise ValueError(f"Function {func_.__name__} cannot be applied: {e}")

# timed call
async def tcall(input_: Any, func: Callable, sleep: float = 0.1,
                  message: Optional[str] = None, ignore_error: bool = False, 
                  include_timing: bool = False, **kwargs
        ) -> Union[Any, Tuple[Any, float]]:
    """
    Timed call: Handle both synchronous and asynchronous calls with optional delay, error handling, and execution timing.

    Args:
        input_ (Any): The input to be passed to the function.
        func (Callable): The (async) function to be called.
        sleep (float, optional): Delay before the function call in seconds.
        message (Optional[str], optional): Custom message for error handling.
        ignore_error (bool, optional): If False, re-raises the caught exception.
        include_timing (bool, optional): If True, returns execution duration.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, optionally with execution duration.

    Raises:
        Exception: If the function raises an exception and ignore_error is False.

    Examples:
        >>> async def my_func(x): return x * 2
        >>> asyncio.run(tcall(3, my_func))
        6
        >>> asyncio.run(tcall(3, my_func, include_timing=True))
        (6, <execution_duration>)
    """
    async def async_call() -> Tuple[Any, float]:
        start_time = time.time()
        try:
            await asyncio.sleep(sleep)
            result = await func(input_, **kwargs)
            duration = time.time() - start_time
            return (result, duration) if include_timing else result
        except Exception as e:
            handle_error(e)

    def sync_call() -> Tuple[Any, float]:
        start_time = time.time()
        try:
            time.sleep(sleep)
            result = func(input_, **kwargs)
            duration = time.time() - start_time
            return (result, duration) if include_timing else result
        except Exception as e:
            handle_error(e)

    def handle_error(e: Exception):
        err_msg = f"{message} Error: {e}" if message else f"An error occurred: {e}"
        print(err_msg)
        if not ignore_error:
            raise

    if asyncio.iscoroutinefunction(func):
        return await async_call()
    else:
        return sync_call()

async def mcall(input_: Union[Any, List[Any]], 
                       funcs: Union[Callable, List[Callable]], 
                       explode: bool = False,
                       flatten: bool = False,
                       dropna: bool = False,
                       **kwargs) -> List[Any]:
    """
    mapped call: handles both synchronous and asynchronous function calls
    on input elements with additional features such as flattening, dropping NAs, and
    applying multiple functions to each input.

    Args:
        input_ (Union[Any, List[Any]]): Input or list of inputs.
        funcs (Union[Callable, List[Callable]]): Function or list of functions.
        explode (bool, optional): If True, applies each function to each input.
        flatten (bool, optional): If True, flattens the input list.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments for the function calls.

    Returns:
        List[Any]: List of results from applying function(s) to input(s).

    Examples:
        >>> async def increment(x): return x + 1
        >>> async def double(x): return x * 2
        >>> asyncio.run(mcall([1, 2, 3], [increment, double, increment]))
        [[2], [4], [4]]
        >>> asyncio.run(mcall([1, 2, 3], [increment, double, increment], explode=True))
        [[2, 4, 4], [3, 5, 5], [4, 6, 6]]
    """
    if explode:
        return await _explode_call(input_=input_, funcs=funcs, dropna=dropna, **kwargs)
    else:
        return await _mapped_call(input_=input_, funcs=funcs, flatten=flatten, dropna=dropna, **kwargs)

async def bcall(inputs: List[Any], func: Callable[..., Any], batch_size: int, **kwargs) -> List[Any]:
    """
    batch call: Processes a list of inputs in batches, applying a function (sync or async) to each item in a batch.

    Args:
        inputs (List[Any]): The list of inputs to be processed.
        func (Callable[..., Any]): The function (can be sync or async) to be applied to each item.
        batch_size (int): The number of items to include in each batch.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results from applying the function to each item in the batches.

    Raises:
        Exception: If an exception occurs during batch processing.

    Examples:
        >>> async def add_one(x): return x + 1
        >>> asyncio.run(bcall([1, 2, 3, 4], add_one, batch_size=2))
        [2, 3, 4, 5]
    """

    async def process_batch(batch: List[Any]) -> List[Any]:
        if asyncio.iscoroutinefunction(func):
            # Process asynchronously if the function is a coroutine
            return await asyncio.gather(*(func(item, **kwargs) for item in batch))
        else:
            # Process synchronously otherwise
            return [func(item, **kwargs) for item in batch]

    results = []
    for i in range(0, len(inputs), batch_size):
        batch = inputs[i:i + batch_size]
        try:
            batch_results = await process_batch(batch)
            results.extend(batch_results)
        except Exception as e:
            # Handle exceptions or log errors here if needed
            raise e
    return results

async def rcall(func: Callable[..., Any], *args, timeout: Optional[int] = None,
                 retries: Optional[int] = 0, initial_delay: float = 2.0,
                 backoff_factor: float = 2.0, default: Optional[Any] = None, 
                 **kwargs) -> Any:
    """
    Retry call: Executes a function with optional timeout, retry, and default value mechanisms.

    Args:
        func (Callable[..., Any]): The function to be executed.
        *args: Positional arguments to pass to the function.
        timeout (Optional[int]): Timeout in seconds for the function call.
        retries (Optional[int]): Number of times to retry the function call.
        initial_delay (float): Initial delay in seconds for retries.
        backoff_factor (float): Factor by which the delay is multiplied on each retry.
        default (Optional[Any]): Default value to return in case of an exception.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call, default value if specified, or raises an exception.

    Raises:
        Exception: If the function raises an exception beyond the specified retries.

    Examples:
        >>> async def my_func(x): return x * 2
        >>> asyncio.run(rcall(my_func, 3))
        6
        >>> asyncio.run(rcall(my_func, 3, retries=2, initial_delay=1, backoff_factor=2))
        6
    """
    async def async_call():
        return await asyncio.wait_for(func(*args, **kwargs), timeout) if timeout else await func(*args, **kwargs)

    def sync_call():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                future.cancel()
                raise asyncio.TimeoutError("Function call timed out")

    delay = initial_delay
    for attempt in range((retries+1) or 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await async_call()
            else:
                return sync_call()
        except Exception as e:
            if attempt >= retries:
                if default is not None:
                    return default
                raise e
            await asyncio.sleep(delay)
            delay *= backoff_factor


class CallDecorator:
    
    @staticmethod
    def cache(func: Callable) -> Callable:
        """
        Decorator that caches the results of function calls (both sync and async). 
        If the function is called again with the same arguments, 
        the cached result is returned instead of re-executing the function.

        Args:
            func (Callable): The function (can be sync or async) whose results need to be cached.

        Returns:
            Callable: A decorated function with caching applied.
        """

        if asyncio.iscoroutinefunction(func):
            # Asynchronous function handling
            @cached(ttl=10 * 60)
            async def cached_async(*args, **kwargs) -> Any:
                return await func(*args, **kwargs)
            
            @ft.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                return await cached_async(*args, **kwargs)

            return async_wrapper

        else:
            # Synchronous function handling
            @ft.lru_cache(maxsize=None)
            def cached_sync(*args, **kwargs) -> Any:
                return func(*args, **kwargs)
            
            @ft.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                return cached_sync(*args, **kwargs)

            return sync_wrapper

    @staticmethod
    def timeout(timeout: int) -> Callable:
        """
        Decorator to apply a timeout to a function.

        Args:
            timeout (int): Maximum execution time allowed for the function in seconds.

        Returns:
            Callable: A decorated function with a timeout mechanism applied.
        """
        def decorator(func: Callable[..., Any]) -> Callable:
            @ft.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                return await rcall(func, *args, timeout=timeout, **kwargs)

            @ft.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                return asyncio.run(rcall(func, *args, timeout=timeout, **kwargs))

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator

    @staticmethod
    def retry(retries: int = 3, initial_delay: float = 2.0, backoff_factor: float = 2.0) -> Callable:
        """
        Decorator to apply a retry mechanism to a function.

        Args:
            retries (int): Maximum number of retry attempts.
            initial_delay (float): Initial delay in seconds before the first retry.
            backoff_factor (float): Factor by which the delay is increased on each retry.

        Returns:
            Callable: A decorated function with a retry mechanism applied.
        """
        def decorator(func: Callable[..., Any]) -> Callable:
            @ft.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                return await rcall(func, *args, retries=retries, initial_delay=initial_delay, backoff_factor=backoff_factor, **kwargs)

            @ft.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                return asyncio.run(rcall(func, *args, retries=retries, initial_delay=initial_delay, backoff_factor=backoff_factor, **kwargs))

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator

    @staticmethod
    def default(default_value: Any) -> Callable:
        """
        Decorator to apply a default value mechanism to a function.

        Args:
            default (Any): The default value to return in case the function execution fails.

        Returns:
            Callable: A decorated function that returns a default value on failure.
        """
        def decorator(func: Callable[..., Any]) -> Callable:
            @ft.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                return await rcall(func, *args, default=default_value, **kwargs)

            @ft.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                return asyncio.run(rcall(func, *args, default=default_value, **kwargs))

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator

    @staticmethod
    def throttle(period: int) -> Callable:
        """
        A decorator factory that creates a throttling decorator for both synchronous and asynchronous functions.

        Args:
            period (int): The minimum time period (in seconds) between successive calls of the decorated function.

        Returns:
            Callable: A decorator that applies a throttling mechanism to the decorated function.

        Usage:
            @throttle(2)
            def my_function():
                # Function implementation

            @throttle(2)
            async def my_async_function():
                # Async function implementation
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            throttle_decorator = Throttle(period)
            if asyncio.iscoroutinefunction(func):
                return throttle_decorator.__call_async__(func)
            else:
                return throttle_decorator(func)
        return decorator

    @staticmethod
    def pre_post_process(preprocess: Callable[..., Any], postprocess: Callable[..., Any]) -> Callable:
        """
        Decorator factory that applies preprocessing and postprocessing to a function (sync or async).

        Args:
            preprocess (Callable[..., Any]): A function to preprocess each argument.
            postprocess (Callable[..., Any]): A function to postprocess the result.

        Returns:
            Callable: A decorator that applies preprocessing and postprocessing to the decorated function.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @ft.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                preprocessed_args = [preprocess(arg) for arg in args]
                preprocessed_kwargs = {k: preprocess(v) for k, v in kwargs.items()}
                result = await func(*preprocessed_args, **preprocessed_kwargs)
                return postprocess(result)

            @ft.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                preprocessed_args = [preprocess(arg) for arg in args]
                preprocessed_kwargs = {k: preprocess(v) for k, v in kwargs.items()}
                result = func(*preprocessed_args, **preprocessed_kwargs)
                return postprocess(result)

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    @staticmethod
    def filter(predicate: Callable[[Any], bool]) -> Callable:
        """
        Decorator factory to filter values returned by a function based on a predicate.

        Args:
            predicate (Callable[[Any], bool]): Predicate function to filter values.

        Returns:
            Callable: Decorated function that filters its return values.
        """
        def decorator(func: Callable[..., List[Any]]) -> Callable:
            @ft.wraps(func)
            def wrapper(*args, **kwargs) -> List[Any]:
                values = func(*args, **kwargs)
                return [value for value in values if predicate(value)]
            return wrapper
        return decorator

    @staticmethod
    def map(function: Callable[[Any], Any]) -> Callable:
        """
        Decorator factory to map values returned by a function using a provided function.

        Args:
            function (Callable[[Any], Any]): Function to map values.

        Returns:
            Callable: Decorated function that maps its return values.
        """
        def decorator(func: Callable[..., List[Any]]) -> Callable:
            @ft.wraps(func)
            def wrapper(*args, **kwargs) -> List[Any]:
                values = func(*args, **kwargs)
                return [function(value) for value in values]
            return wrapper
        return decorator

    @staticmethod
    def reduce(function: Callable[[Any, Any], Any], initial: Any) -> Callable:
        """
        Decorator factory to reduce values returned by a function to a single value using the provided function.

        Args:
            function (Callable[[Any, Any], Any]): Reducing function.
            initial (Any): Initial value for reduction.

        Returns:
            Callable: Decorated function that reduces its return values.
        """
        def decorator(func: Callable[..., List[Any]]) -> Callable:
            @ft.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                values = func(*args, **kwargs)
                return ft.reduce(function, values, initial)
            return wrapper
        return decorator

    @staticmethod
    def compose(*functions: Callable[[Any], Any]) -> Callable:
        """
        Decorator factory that composes multiple functions. The output of each function is passed as 
        the input to the next, in the order they are provided.

        Args:
            *functions: Variable length list of functions to compose.

        Returns:
            Callable: A new function that is the composition of the given functions.
        """
        def decorator(func: Callable) -> Callable:
            @ft.wraps(func)
            def wrapper(*args, **kwargs):
                value = func(*args, **kwargs)
                for function in functions:
                    try:
                        value = function(value)
                    except Exception as e:
                        raise ValueError(f"Error in function {function.__name__}: {e}")
                return value
            return wrapper
        return decorator

    @staticmethod
    def memorize(maxsize: int = 10_000) -> Callable:
        """
        Decorator factory to memorize function calls. Caches the return values of the function for specific inputs.

        Args:
            maxsize (int): Maximum size of the cache. Defaults to 10,000.

        Returns:
            Callable: A memorized version of the function.
        """
        def decorator(function: Callable) -> Callable:
            cache = OrderedDict()
            
            @ft.wraps(function)
            def memorized_function(*args):
                if args in cache:
                    cache.move_to_end(args)  # Move the recently accessed item to the end
                    return cache[args]

                if len(cache) >= maxsize:
                    cache.popitem(last=False)  # Remove oldest cache entry

                result = function(*args)
                cache[args] = result
                return result
            
            return memorized_function
        
        return decorator

    @staticmethod
    def validate(**config):
        """
        Decorator factory to process the return value of a function using specified validation and conversion functions.

        Args:
            **config: Configuration dictionary specifying the processing functions and their settings.

        Returns:
            Callable: A decorator that applies specified processing to the function's return value.
        """
        def decorator(func: Callable) -> Callable:
            @ft.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                value = func(*args, **kwargs)
                return _process_value(value, config)

            return wrapper

        return decorator
    
    @staticmethod
    def max_concurrency(limit: int=5):
        """
        Decorator to limit the maximum number of concurrent executions of an async function.
        
        Args:
            limit (int): The maximum number of concurrent tasks allowed.
        """

        def decorator(func: Callable):
            semaphore = asyncio.Semaphore(limit)

            @ft.wraps(func)
            async def wrapper(*args, **kwargs):
                async with semaphore:
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

def _handle_error(value: Any, config: Dict[str, Any]) -> Any:
    """Handle an error by logging and returning a default value if provided.

    Args:
        value: The value to check for an exception.
        config: A dictionary with optional keys 'log' and 'default'.

    Returns:
        The original value or the default value from config if value is an exception.

    Examples:
        >>> handle_error(ValueError("An error"), {'log': True, 'default': 'default_value'})
        Error: An error
        'default_value'
    """
    if isinstance(value, Exception):
        if config.get('log', True):
            print(f"Error: {value}")  # Replace with appropriate logging mechanism
        return config.get('default', None)
    return value

def _validate_type(value: Any, expected_type: Type) -> Any:
    """Validate the type of value, raise TypeError if not expected type.

    Args:
        value: The value to validate.
        expected_type: The type that value is expected to be.

    Returns:
        The original value if it is of the expected type.

    Raises:
        TypeError: If value is not of the expected type.

    Examples:
        >>> validate_type(10, int)
        10
        >>> validate_type("10", int)
        Traceback (most recent call last):
        ...
        TypeError: Invalid type: expected <class 'int'>, got <class 'str'>
    """
    if not isinstance(value, expected_type):
        raise TypeError(f"Invalid type: expected {expected_type}, got {type(value)}")
    return value

def _convert_type(value: Any, target_type: Callable) -> Optional[Any]:
    """Convert the type of value to target_type, return None if conversion fails.

    Args:
        value: The value to convert.
        target_type: The type to convert value to.

    Returns:
        The converted value or None if conversion fails.

    Examples:
        >>> convert_type("10", int)
        10
        >>> convert_type("abc", int)
        Conversion error: invalid literal for int() with base 10: 'abc'
        None
    """
    try:
        return target_type(value)
    except (ValueError, TypeError) as e:
        print(f"Conversion error: {e}")  # Replace with appropriate logging mechanism
        return None

def _process_value(value: Any, config: Dict[str, Any]) -> Any:
    """
    Processes a value using a chain of functions defined in config.
    """
    processing_functions = {
        'handle_error': _handle_error,
        'validate_type': _validate_type,
        'convert_type': _convert_type
    }

    try:
        for key, func_config in config.items():
            func = processing_functions.get(key)
            if func:
                value = func(value, func_config)
        return value
    except Exception as e:
        if 'handle_error' in config.keys():
            func = processing_functions.get('handle_error')
            return func(e, config['handle_error'])
        else:
            raise e

async def _mapped_call(input_: Union[Any, List[Any]], 
                       funcs: Union[Callable, List[Callable]], 
                       flatten: bool = False,
                       dropna: bool = False,
                       **kwargs) -> List[Any]:

    input_ = to_list(input_=input_, flatten=flatten, dropna=dropna)
    funcs = to_list(funcs)
    assert len(input_) == len(funcs), "The number of inputs and functions must be the same."
    return to_list(
            [
                await alcall(input_=inp, func_=f, flatten=flatten, dropna=dropna, **kwargs) 
                for f, inp in zip(funcs, input_)
            ]
        )
    
async def _explode_call(input_: Union[Any, List[Any]], 
                       funcs: Union[Callable, List[Callable]], 
                       dropna: bool = False,
                       **kwargs) -> List[Any]:

    async def _async_f(x, y):
        return await mcall(
            create_copy(x, len(to_list(y))), y, flatten=False, dropna=dropna, **kwargs
            )

    tasks = [_async_f(inp, funcs) for inp in to_list(input_)]    
    return await asyncio.gather(*tasks)

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
        @ft.wraps(func)
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
        @ft.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - self.last_called
            if elapsed < self.period:
                await asyncio.sleep(self.period - elapsed)
            self.last_called = time.time()
            return await func(*args, **kwargs)

        return wrapper



# # parallel call with control of max_concurrent 
# async def pcall(input_: Any, 
#                        funcs: Union[Callable, List[Callable]], 
#                        max_concurrent: Optional[int] = None,
#                        flatten: bool = False, 
#                        dropna: bool = False, 
#                        **kwargs) -> List[Any]:
#     """
#     A unified function that handles both synchronous and asynchronous function calls
#     on input elements. It can process inputs in parallel or sequentially and can handle
#     both single and multiple functions with corresponding inputs.

#     Args:
#         input_ (Any): The input to process, potentially a list.
#         funcs (Union[Callable, List[Callable]]): A function or list of functions to apply.
#         max_concurrent (Optional[int]): Maximum number of concurrent executions for parallel processing.
#         flatten (bool): If True, flattens the input.
#         dropna (bool): If True, drops None values from the list.
#         **kwargs: Additional keyword arguments to pass to the function(s).

#     Returns:
#         List[Any]: A list containing the results of function call(s) on input elements.
#     """

#     async def async_wrapper(func, item):
#         return await func(item, **kwargs) if asyncio.iscoroutinefunction(func) else func(item, **kwargs)

#     try:
#         lst = to_list(input_=input_, flatten=flatten, dropna=dropna)
#         if not isinstance(funcs, list):
#             funcs = [funcs] * len(lst)
#         tasks = [async_wrapper(func, item) for func, item in zip(funcs, lst)]
#         if max_concurrent:
#             semaphore = asyncio.Semaphore(max_concurrent)
#             async with semaphore:
#                 return await asyncio.gather(*tasks)
#         else:
#             return await asyncio.gather(*tasks)
#     except Exception as e:
#         raise ValueError(f"Error in unified_call: {e}")
