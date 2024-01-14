import asyncio
import time
from functools import lru_cache, wraps
from typing import Any, Callable, Iterable, List, Optional, Tuple, Union
from .sys_util import create_copy, to_list

# list call
def lcall(input_: Any, func_: Callable, flatten: bool = False,
          dropna: bool = False, **kwargs) -> List[Any]:
    """
    Applies a function to each element in a list, with options for flattening and dropping NAs.

    Args:
        input_ (Any): The input, potentially a list, to process.
        func_ (Callable): The function to be applied to each element.
        flatten (bool, optional): If True, flattens the input.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list containing the results of the function call on each element.
    """
    try:
        lst = to_list(input_=input_, flatten=flatten, dropna=dropna)
        return [func_(i, **kwargs) for i in lst]
    except Exception as e:
        raise ValueError(f"Function {func_.__name__} cannot be applied: {e}")

async def alcall(input_: Any, func_: Callable, flatten: bool = False, dropna: bool = True, **kwargs) -> List[Any]:
    """
    Asynchronously or synchronously applies a function to each element in a list, 
    with options for flattening and dropping NAs.

    Args:
        input_ (Any): The input, potentially a list, to process.
        func_ (Callable): The function (can be async or sync) to be applied to each element.
        flatten (bool, optional): If True, flattens the input.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list containing the results of the function call on each element.
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
def tcall(input_: Any, func: Callable, sleep: float = 0.1,
                  message: Optional[str] = None, ignore_error: bool = False, 
                  include_timing: bool = False, **kwargs) -> Union[Any, Tuple[Any, float]]:
    """
    Enhanced function to handle both synchronous and asynchronous calls with 
    optional delay, error handling, and execution timing.

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
        return asyncio.run(async_call())
    else:
        return sync_call()

# parallel call with control of max_concurrent 
async def pcall(input_: Any, 
                       funcs: Union[Callable, List[Callable]], 
                       max_concurrent: Optional[int] = None,
                       flatten: bool = False, 
                       dropna: bool = False, 
                       **kwargs) -> List[Any]:
    """
    A unified function that handles both synchronous and asynchronous function calls
    on input elements. It can process inputs in parallel or sequentially and can handle
    both single and multiple functions with corresponding inputs.

    Args:
        input_ (Any): The input to process, potentially a list.
        funcs (Union[Callable, List[Callable]]): A function or list of functions to apply.
        max_concurrent (Optional[int]): Maximum number of concurrent executions for parallel processing.
        flatten (bool): If True, flattens the input.
        dropna (bool): If True, drops None values from the list.
        **kwargs: Additional keyword arguments to pass to the function(s).

    Returns:
        List[Any]: A list containing the results of function call(s) on input elements.
    """

    async def async_wrapper(func, item):
        return await func(item, **kwargs) if asyncio.iscoroutinefunction(func) else func(item, **kwargs)

    try:
        lst = to_list(input_=input_, flatten=flatten, dropna=dropna)
        if not isinstance(funcs, list):
            funcs = [funcs] * len(lst)
        tasks = [async_wrapper(func, item) for func, item in zip(funcs, lst)]
        if max_concurrent:
            semaphore = asyncio.Semaphore(max_concurrent)
            async with semaphore:
                return await asyncio.gather(*tasks)
        else:
            return await asyncio.gather(*tasks)
    except Exception as e:
        raise ValueError(f"Error in unified_call: {e}")

# mapped call
async def mcall(input_: Union[Any, List[Any]], 
                       funcs: Union[Callable, List[Callable]], 
                       explode: bool = False,
                       flatten: bool = True, 
                       dropna: bool = True, 
                       **kwargs) -> List[Any]:
    """
    A unified function that handles both synchronous and asynchronous function calls
    on input elements with additional features such as flattening, dropping NAs, and
    applying multiple functions to each input.

    Args:
        input_ (Union[Any, List[Any]]): Input or list of inputs.
        funcs (Union[Callable, List[Callable]]): Function or list of functions.
        expand_combinations (bool, optional): If True, applies each function to each input.
        flatten (bool, optional): If True, flattens the input list.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments for the function calls.

    Returns:
        List[Any]: List of results from applying function(s) to input(s).
    """

    async def async_wrapper(func, item):
        return await func(item, **kwargs) if asyncio.iscoroutinefunction(func) else func(item, **kwargs)

    inputs = to_list(input_, flatten=flatten)
    if dropna:
        inputs = [i for i in inputs if i is not None]

    if explode:
        funcs = to_list(funcs)
        inputs = [create_copy(inp, len(funcs)) for inp in inputs]
        inputs = [item for sublist in inputs for item in sublist]  # Flatten the list
    else:
        if not isinstance(funcs, list):
            funcs = [funcs] * len(inputs)

    tasks = [async_wrapper(f, i) for f, i in zip(funcs, inputs)]
    return await asyncio.gather(*tasks)

# batch call
async def bcall(func: Callable[..., Any], inputs: List[Any], batch_size: int, **kwargs) -> List[Any]:
    """
    Processes a list of inputs in batches, applying a function (sync or async) to each item in a batch.

    Args:
        func (Callable[..., Any]): The function (can be sync or async) to be applied to each item.
        inputs (List[Any]): The list of inputs to be processed.
        batch_size (int): The number of items to include in each batch.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results from applying the function to each item in the batches.
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

# retry call
def rcall(func: Callable[..., Any], *args, timeout: Optional[int] = None, 
                 retries: Optional[int] = None, initial_delay: float = 2.0, 
                 backoff_factor: float = 2.0, default: Optional[Any] = None, 
                 **kwargs) -> Any:
    """
    Executes a function with optional timeout, retry, and default value mechanisms.

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
    """
    async def async_call():
        return await asyncio.wait_for(func(*args, **kwargs), timeout) if timeout else await func(*args, **kwargs)

    try:
        delay = initial_delay
        for attempt in range(retries or 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    loop = asyncio.get_event_loop()
                    return loop.run_until_complete(async_call())
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                if retries is None or attempt >= retries - 1:
                    raise e
                time.sleep(delay)
                delay *= backoff_factor
    except Exception as e:
        if default is not None:
            return default
        raise e

# decorators
def cache_results(func: Callable) -> Callable:
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
        @lru_cache(maxsize=None)
        async def cached_async(*args, **kwargs) -> Any:
            return await func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            return await cached_async(*args, **kwargs)

        return async_wrapper

    else:
        # Synchronous function handling
        @lru_cache(maxsize=None)
        def cached_sync(*args, **kwargs) -> Any:
            return func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            return cached_sync(*args, **kwargs)

        return sync_wrapper

def time_spent(func: Callable[..., Any]) -> Callable[..., Tuple[Any, float]]:
    """
    Decorator that measures the execution time of a function.

    When applied to a function, it wraps the function call and returns a tuple containing
    the original function's result and the time taken to execute the function in seconds.

    Args:
        func (Callable[..., Any]): The function to be timed.

    Returns:
        Callable[..., Tuple[Any, float]]: A wrapper function that returns a tuple of 
        the function's result and its execution duration in seconds.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[Any, float]:
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        return result, duration

    return wrapper

def timeout(timeout: int) -> Callable:
    """
    Decorator to apply a timeout to a function.

    If the function's execution time exceeds the specified timeout, it will be terminated, and a TimeoutError is raised.

    Args:
        timeout (int): Maximum execution time allowed for the function in seconds.

    Returns:
        Callable: A decorated function with a timeout mechanism applied.

    Usage:
        @timeout(5)
        def my_function(arg1, arg2):
            # Function implementation
            pass

    This will apply a 5-second timeout to `my_function`.
    """
    def decorator(func: Callable[..., Any]) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return rcall(func, *args, timeout=timeout, **kwargs)
        return wrapper
    return decorator

def retry(retries: int = 3, initial_delay: float = 2.0, backoff_factor: float = 2.0) -> Callable:
    """
    Decorator to apply a retry mechanism to a function.

    If the function raises an exception, it will be retried up to the specified number of times with an exponential backoff delay.

    Args:
        retries (int): Maximum number of retry attempts.
        initial_delay (float): Initial delay in seconds before the first retry.
        backoff_factor (float): Factor by which the delay is increased on each retry.

    Returns:
        Callable: A decorated function with a retry mechanism applied.

    Usage:
        @retry(retries=3, initial_delay=1, backoff_factor=2)
        def my_function(arg1, arg2):
            # Function implementation
            pass

    This will retry `my_function` up to 3 times with increasing delays if it raises an exception.
    """
    def decorator(func: Callable[..., Any]) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return rcall(func, *args, retries=retries, initial_delay=initial_delay, backoff_factor=backoff_factor, **kwargs)
        return wrapper
    return decorator

def default_value(default: Any) -> Callable:
    """
    Decorator to apply a default value mechanism to a function.

    If the function raises an exception, instead of propagating the exception, it returns a specified default value.

    Args:
        default (Any): The default value to return in case the function execution fails.

    Returns:
        Callable: A decorated function that returns a default value on failure.

    Usage:
        @default_value(default=0)
        def my_function(arg1, arg2):
            # Function implementation
            pass

    If `my_function` raises an exception, it will return 0 instead of propagating the exception.
    """
    def decorator(func: Callable[..., Any]) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return rcall(func, *args, default=default, **kwargs)
        return wrapper
    return decorator

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
        @wraps(func)
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
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - self.last_called
            if elapsed < self.period:
                await asyncio.sleep(self.period - elapsed)
            self.last_called = time.time()
            return await func(*args, **kwargs)

        return wrapper

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
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            preprocessed_args = [preprocess(arg) for arg in args]
            preprocessed_kwargs = {k: preprocess(v) for k, v in kwargs.items()}
            result = await func(*preprocessed_args, **preprocessed_kwargs)
            return postprocess(result)

        @wraps(func)
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
