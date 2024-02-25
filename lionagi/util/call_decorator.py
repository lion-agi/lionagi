import asyncio
import functools
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, List

from aiocache import cached

from .call_util import is_coroutine_func, rcall


class CallDecorator:
    """
    Provides a collection of decorators to enhance asynchronous function calls with
    additional behaviors such as timeouts, retries, throttling, and more. These
    decorators are designed to support both synchronous and asynchronous functions,
    allowing for flexible and efficient execution patterns in a variety of contexts.

    The decorators include functionality for applying timeouts, retrying with
    exponential backoff, limiting concurrency, caching results, and preprocessing or
    postprocessing inputs and outputs. They can be applied directly to functions or
    methods to modify their behavior without altering the original logic.

    Usage of these decorators simplifies the management of asynchronous operations,
    making it easier to implement robust error handling, rate limiting, and result
    caching. This is particularly beneficial in environments where operations are
    I/O-bound and can greatly benefit from asynchronous execution.
    """

    @staticmethod
    def timeout(timeout: int) -> Callable:
        """
        Applies a timeout to an asynchronous function call, ensuring that the function
        execution completes within the specified duration.

        This decorator is crucial for operations where a strict execution time limit is
        required. It prevents the function from running indefinitely by raising an
        asyncio.TimeoutError if the execution time exceeds the specified timeout.

        Args:
            timeout (int):
                The maximum duration, in seconds, that the function is allowed to execute.

        Returns:
            Callable:
                A decorated function that enforces the specified execution timeout.

        Examples:
            >>> @CallDecorator.timeout(5)
            ... async def long_running_task():
            ...     # Implementation that may exceed the timeout duration
            ...     await asyncio.sleep(10)
            ...     return "Completed"
            ... # Executing `long_running_task` will raise an asyncio.TimeoutError after 5
            ... # seconds
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
        Decorates an asynchronous function to automatically retry on failure,
        with configurable retries, delay, and exponential backoff.

        This decorator is useful for handling operations that may fail due to transient
        issues, such as network connectivity problems or temporary provider
        unavailability. By automatically retrying the function call, it increases the
        robustness of the application without complicating the core logic with retry
        mechanisms.

        Args:
            retries (int, optional):
                The number of retry attempts before giving up. Defaults to 3.
            delay (float, optional):
                The initial delay between retries, in seconds. Defaults to 2.0.
            backoff_factor (float, optional):
                The multiplier applied to the delay for each subsequent retry, for
                exponential backoff. Default to 2.0.

        Returns:
            Callable:
                A decorated asynchronous function with retry logic based on the specified
                parameters.

        Examples:
            >>> @CallDecorator.retry(retries=2, delay=1, backoff_factor=2)
            ... async def fetch_data():
            ...     # Implementation that might fail transiently
            ...     raise ConnectionError("Temporary failure")
            ... # `fetch_data` will automatically retry on ConnectionError, up to 2 times,
            ... # with delays of 1s and 2s.
        """

        def decorator(func: Callable[..., Any]) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await rcall(
                    func,
                    *args,
                    retries=retries,
                    delay=delay,
                    backoff_factor=backoff_factor,
                    **kwargs,
                )

            return wrapper

        return decorator

    @staticmethod
    def default(default_value: Any) -> Callable:
        """
        Decorates an asynchronous function to return a default value in case of an
        exception, allowing the function to gracefully handle errors without
        interrupting the application flow.

        This decorator simplifies error handling by encapsulating the try-except logic
        within the decoration process, providing a default result when an operation
        fails. This is particularly useful for non-critical operations where a fallback
        value can prevent the application from crashing or halting due to minor errors.

        Args:
            default_value (Any):
                The value to return if the decorated function raises an exception.

        Returns:
            Callable:
                A decorated asynchronous function that returns `default_value` in case of
                error.

        Examples:
            >>> @CallDecorator.default(default_value="Fetch failed")
            ... async def get_resource():
            ...     # Implementation that might raise an exception
            ...     raise RuntimeError("Resource not available")
            ... # Executing `get_resource` will return "Fetch failed" instead of raising
            ... # an error
        """

        def decorator(func: Callable[..., Any]) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await rcall(func, *args, default=default_value, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def throttle(period: int) -> Callable:
        """
        Decorates an asynchronous function to limit its execution frequency to not
        exceed one call per specified period. This is useful for rate-limiting calls to
        external services, APIs, or any operation where maintaining a maximum call
        frequency is required to avoid overloading resources or hitting API rate limits.

        The throttling is achieved by introducing a delay if the time elapsed since the
        last call is less than the specified period. This ensures that the decorated
        function does not execute more frequently than the allowed rate.

        Args:
            period (int):
                The minimum time interval, in seconds, between consecutive calls to the
                decorated function.

        Returns:
            Callable:
                A decorated asynchronous function that adheres to the specified call
                frequency limit.

        Examples:
            >>> @CallDecorator.throttle(2)
            ... async def fetch_data():
            ...     # Implementation that fetches data from an external source
            ...     pass
            ... # `fetch_data` will not be called more often than once every 2 seconds.
        """
        return _Throttle(period)

    @staticmethod
    def map(function: Callable[[Any], Any]) -> Callable:
        """
        Decorates an asynchronous function to apply a specified mapping function to
        each element in the list returned by the decorated function. This is
        particularly useful for post-processing the results of asynchronous operations,
        such as transforming data fetched from an API or processing items in a
        collection concurrently.

        The mapping function is applied to each item in the output list of the
        decorated function, enabling patterned modifications or transformations to be
        succinctly applied to a collection of asynchronous results.

        Args:
            function (Callable[[Any], Any]):
                A mapping function to apply to each element of the list returned by the
                decorated function.

        Returns:
            Callable:
                A decorated asynchronous function whose results are transformed by the
                specified mapping function.

        Examples:
            >>> @CallDecorator.map(lambda x: x.upper())
            ... async def get_names():
            ...     # Asynchronously fetches a list of names
            ...     return ["alice", "bob", "charlie"]
            ... # `get_names` now returns ["ALICE", "BOB", "CHARLIE"]
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
        Creates a decorator to sequentially apply multiple functions, where the output
        of one function becomes the input to the next. This enables function
        composition, allowing for elegant and flexible chaining of operations.

        This decorator is particularly useful when you need to perform a series of
        transformations or operations on data, especially when those operations need to
        be applied in a specific order. It supports both synchronous and asynchronous
        functions but requires all functions to be of the same type (all synchronous or
        all asynchronous).

        Args:
            *functions (Callable[[Any], Any]):
                A variable number of functions that are to be composed together. Each
                function must accept a single argument and return a value.

        Returns:
            Callable:
                A decorator that, when applied to a function, composes it with the
                specified functions, creating a pipeline of function calls.

        Raises:
            ValueError:
                If the provided functions mix synchronous and asynchronous types, as they
                cannot be composed together.

        Examples:
            >>> def double(x): return x * 2
            >>> def increment(x): return x + 1
            >>> @CallDecorator.compose(increment, double)
            ... def start_value(x):
            ...     return x
            >>> start_value(3)
            7  # The value is doubled to 6, then incremented to 7
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
                            raise ValueError(
                                f"Error in function {function.__name__}: {e}"
                            )
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
                            raise ValueError(
                                f"Error in function {function.__name__}: {e}"
                            )
                    return value

                return async_wrapper
            else:
                raise ValueError(
                    "Cannot compose both synchronous and asynchronous functions."
                )

        return decorator

    @staticmethod
    def pre_post_process(
        preprocess: Callable[..., Any], postprocess: Callable[..., Any]
    ) -> Callable:
        """
        Decorates a function with preprocessing and postprocessing steps, allowing for
        modifications to the arguments before the function call and to the result after
        the function call. This decorator is versatile, supporting both synchronous and
        asynchronous functions, and enhances the modularity and reusability of code by
        abstracting common preprocessing and postprocessing patterns into decorator form.

        Preprocessing can include any modifications or checks to the arguments, such as
        validation or transformation, while postprocessing allows for adjustments to the
        function's output, such as formatting results or applying additional computations.

        Args:
            preprocess (Callable[..., Any]):
                A function to preprocess the arguments passed to the decorated function.
                It must accept the same arguments as the decorated function.
            postprocess (Callable[..., Any]):
                A function to postprocess the result of the decorated function. It must
                accept a single argument, which is the output of the decorated function.

        Returns:
            Callable:
                A decorated function that applies the specified preprocessing and
                postprocessing steps to its execution.

        Examples:
            >>> @CallDecorator.pre_post_process(lambda x: x - 1, lambda x: x * 2)
            ... async def process_value(x):
            ...     return x + 2
            >>> asyncio.run(process_value(5))
            12  # Input 5 is preprocessed to 4, processed to 6, and postprocessed to 12
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
        Decorates a function (synchronous or asynchronous) to cache its results for a
        specified time-to-live (TTL). This caching mechanism prevents re-execution of
        the function with the same arguments, improving efficiency, especially for I/O
        bound or computationally intensive operations.

        Args: func (Callable): The target function to cache. Can be either synchronous
        or asynchronous. ttl (int, optional): The time-to-live of the cache entries in
        seconds. Defaults to 600 seconds. maxsize (Optional[int], optional): The
        maximum size of the cache. If None, the cache is unbounded. Applies only to
        synchronous functions.

        Returns:
            Callable: A decorated version of the function with caching applied. Subsequent
            calls with the same arguments within the TTL will return the cached result.

        Examples:
            >>> @CallDecorator.cache(ttl=10)
            ... async def fetch_data(key):
            ...     # Simulate a database fetch
            ...     return "data for " + key
            ... # Subsequent calls to `fetch_data` with the same `key` within 10 seconds
            ... # will return the cached result without re-executing the function body.
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
        Decorates a function to filter its list result based on a given predicate. The
        predicate determines which items in the list should be included in the final
        result. This decorator can be applied to both synchronous and asynchronous
        functions returning lists.

        Args:
            predicate (Callable[[Any], bool]):
                A function that evaluates each item in the list. Items for which the
                predicate returns True are included in the final result.

        Returns:
            Callable:
            A decorated function that filters its list result according to the predicate.

        Examples:
            >>> @CallDecorator.filter(lambda x: x % 2 == 0)
            ... async def get_even_numbers():
            ...     return [1, 2, 3, 4, 5]
            >>> asyncio.run(get_even_numbers())
            [2, 4]
            ... # The result list is filtered to include only even numbers.
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
        Decorates a function to apply a reduction to its list result, combining all
        items in the list into a single value using the specified reduction function.
        This is useful for aggregating results or performing cumulative operations on
        the list returned by the decorated function. The decorator supports both
        synchronous and asynchronous functions.

        Args:
            function (Callable[[Any, Any], Any]):
                The reduction function to apply to the list. It should take two arguments
                and return a single value that is the result of combining them.
            initial (Any):
                The initial value for the reduction process. This value is used as the
                starting point for the reduction and should be an identity value for the
                reduction operation.

        Returns:
            Callable:
                A decorated function that applies the specified reduction to its list
                result,
            producing a single aggregated value.

        Examples:
            >>> @CallDecorator.reduce(lambda x, y: x + y, 0)
            ... async def sum_numbers():
            ...     return [1, 2, 3, 4]
            >>> asyncio.run(sum_numbers())
            10
            ... # The numbers in the list are summed, resulting in a single value.
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
        Limits the number of concurrent executions for an asynchronous function to
        ensure that no more than a specified number of instances of the function run
        simultaneously. This is particularly useful for controlling resource usage and
        preventing overload when dealing with IO-bound operations or external services
        that can only handle a limited amount of concurrent requests.

        Args:
            limit (int):
                The maximum number of concurrent executions allowed for the decorated
                function.

        Returns:
            Callable:
                An asynchronous function wrapper that enforces the concurrency limit.

        Examples:
            >>> @CallDecorator.max_concurrency(3)
            ... async def process_data(item):
            ...     # Asynchronous processing logic here
            ...     pass
            ... # No more than 3 instances of `process_data` will run concurrently.
        """

        def decorator(func: Callable) -> Callable:
            if not asyncio.iscoroutinefunction(func):
                raise TypeError(
                    "max_concurrency decorator can only be used with async functions."
                )
            semaphore = asyncio.Semaphore(limit)

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                async with semaphore:
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    # noinspection PyRedeclaration
    @staticmethod
    def throttle(period: int) -> Callable:
        """
        A static method to create a throttling decorator. This method utilizes the
        _Throttle class to enforce a minimum time period between successive calls of the
        decorated function.

        Args:
            period (int):
                The minimum time period, in seconds, that must elapse between successive
                calls to the decorated function.

        Returns:
            Callable:
                A decorator that applies a throttling mechanism to the decorated function,
                ensuring that the function is not called more frequently than the
                specified period.

        Examples:
            >>> @CallDecorator.throttle(2)  # Ensures at least 2 seconds between calls
            ... async def fetch_data(): pass

            This decorator is particularly useful in scenarios like rate-limiting API
            calls or reducing the frequency of resource-intensive operations.
        """
        return _Throttle(period)

    @staticmethod
    def force_async(fn):
        pool = ThreadPoolExecutor()

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            future = pool.submit(fn, *args, **kwargs)
            return asyncio.wrap_future(future)  # make it awaitable

        return wrapper


class _Throttle:
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
        Initializes a new instance of _Throttle.

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
