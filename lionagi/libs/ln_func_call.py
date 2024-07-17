"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import annotations

from lion_core import CoreLib, LN_UNDEFINED

from functools import wraps, lru_cache, reduce
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
import aiocache
from typing import Any, Callable, AsyncGenerator, Sequence, TypeVar

from typing_extensions import deprecated

from lionagi.libs.ln_convert import to_list


T = TypeVar("T")
ErrorHandler = Callable[[Exception], None]


class lcall:

    @staticmethod
    def __call__(
        input_: Any,
        /,
        func: Callable,
        *,
        flatten: bool = False,
        dropna: bool = False,
        **kwargs,
    ) -> Any:
        lst = to_list(input_, dropna=dropna)
        if len(to_list(func)) != 1:
            raise ValueError(
                "There must be one and only one function for list calling."
            )

        return to_list([func(i, **kwargs) for i in lst], flatten=flatten, dropna=dropna)

    @staticmethod
    async def __async_call__(*args: Any, **kwds: Any) -> Any:
        return await CoreLib.lcall(*args, **kwds)


@deprecated  # Deprecated in favor of lcall, use await lcall instead
async def alcall(
    func: Callable,
    input_: list[Any],
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = LN_UNDEFINED,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, Callable[[Exception], Any]] | None = None,
    max_concurrent: int | None = None,
    throttle_period: float | None = None,
    dropna: bool = False,
    **kwargs: Any,
) -> list:
    """
    Apply a function over a list of inputs asynchronously with options.

    Args:
        func: The function to be applied to each input.
        input_: List of inputs to be processed.
        retries: Number of retry attempts for each function call.
        initial_delay: Initial delay before starting execution.
        delay: Delay between retry attempts.
        backoff_factor: Factor by which delay increases after each attempt.
        default: Default value to return if all attempts fail.
        timeout: Timeout for each function execution.
        timing: Whether to return the execution duration.
        verbose: Whether to print retry messages.
        error_msg: Custom error message.
        error_map: Dictionary mapping exception types to error handlers.
        max_concurrent: Maximum number of concurrent executions.
        throttle_period: Minimum time period between function executions.
        dropna: Whether to drop None values from the output list.
        **kwargs: Additional keyword arguments for the function.

    Returns:
        List of results, optionally including execution durations if timing
        is True.
    """
    return await CoreLib.lcall(
        func,
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
        dropna=dropna,
        **kwargs,
    )


async def pcall(
    funcs: Sequence[Callable[..., T]],
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = LN_UNDEFINED,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, Callable[[Exception], Any]] | None = None,
    max_concurrent: int | None = None,
    throttle_period: float | None = None,
    **kwargs: Any,
) -> list:
    """
    Execute multiple functions asynchronously with customizable options.

    Args:
        funcs: Sequence of functions to be executed.
        retries: Number of retry attempts for each function.
        initial_delay: Initial delay before starting the execution.
        delay: Delay between retry attempts.
        backoff_factor: Factor by which delay increases after each attempt.
        default: Default value to return if all attempts fail.
        timeout: Timeout for each function execution.
        timing: Whether to return the execution duration.
        verbose: Whether to print retry messages.
        error_msg: Custom error message.
        error_map: Dictionary mapping exception types to error handlers.
        max_concurrent: Maximum number of concurrent executions.
        throttle_period: Minimum time period between function executions.
        **kwargs: Additional keyword arguments for each function.

    Returns:
        List of results, optionally including execution durations if timing
        is True.
    """
    return await CoreLib.pcall(
        funcs,
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


async def mcall(
    input_: Any,
    /,
    func: Callable[..., T] | Sequence[Callable[..., T]],
    *,
    explode: bool = False,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = LN_UNDEFINED,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, ErrorHandler] | None = None,
    max_concurrent: int | None = None,
    throttle_period: float | None = None,
    dropna: bool = False,
    **kwargs: Any,
) -> list[T] | list[tuple[T, float]]:
    """
    Apply functions over inputs asynchronously with customizable options.

    Args:
        input_: The input data to be processed.
        func: The function or sequence of functions to be applied.
        explode: Whether to apply each function to all inputs.
        retries: Number of retry attempts for each function call.
        initial_delay: Initial delay before starting execution.
        delay: Delay between retry attempts.
        backoff_factor: Factor by which delay increases after each attempt.
        default: Default value to return if all attempts fail.
        timeout: Timeout for each function execution.
        timing: Whether to return the execution duration.
        verbose: Whether to print retry messages.
        error_msg: Custom error message.
        error_map: Dictionary mapping exception types to error handlers.
        max_concurrent: Maximum number of concurrent executions.
        throttle_period: Minimum time period between function executions.
        dropna: Whether to drop None values from the output list.
        **kwargs: Additional keyword arguments for the functions.

    Returns:
        List of results, optionally including execution durations if timing
        is True.

    Raises:
        ValueError: If the length of inputs and functions don't match when
            not exploding the function calls.
    """
    return await CoreLib.mcall(
        input_,
        func,
        explode=explode,
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
        dropna=dropna,
        **kwargs,
    )


async def bcall(
    input_: Any,
    func: Callable[..., T],
    batch_size: int,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = None,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, ErrorHandler] | None = None,
    max_concurrent: int | None = None,
    throttle_period: float | None = None,
    **kwargs: Any,
) -> AsyncGenerator[list[T | tuple[T, float]], None]:
    """
    Asynchronously call a function in batches with retry and timing options.

    Args:
        input_: The input data to process.
        func: The function to call.
        batch_size: The size of each batch.
        retries: The number of retries.
        initial_delay: Initial delay before the first attempt in seconds.
        delay: The delay between retries in seconds.
        backoff_factor: Factor by which delay increases after each retry.
        default: Default value to return if an error occurs.
        timeout: The timeout for the function call in seconds.
        timing: If True, return execution time along with the result.
        verbose: If True, print retry attempts and exceptions.
        error_msg: Custom error message prefix.
        error_map: Mapping of errors to handle custom error responses.
        max_concurrent: Maximum number of concurrent calls.
        throttle_period: Throttle period in seconds.
        **kwargs: Additional keyword arguments to pass to the function.

    Yields:
        A list of results for each batch of inputs.

    Examples:
        >>> async def sample_func(x):
        ...     return x * 2
        >>> async for batch_results in bcall([1, 2, 3, 4, 5], sample_func, 2,
        ...                                  retries=3, delay=1):
        ...     print(batch_results)
    """
    return await CoreLib.bcall(
        input_,
        func,
        batch_size,
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


async def tcall(
    func: Callable[..., T],
    *args: Any,
    initial_delay: float = 0,
    error_msg: str | None = None,
    suppress_err: bool = False,
    timing: bool = False,
    timeout: float | None = None,
    default: Any = None,
    error_map: dict[type, ErrorHandler] | None = None,
    **kwargs: Any,
) -> T | tuple[T, float]:
    """
    Execute a function asynchronously with customizable options.

    Handles both synchronous and asynchronous functions, applying initial
    delay, timing execution, handling errors, and enforcing timeout.

    Args:
        func: The function to be executed.
        *args: Positional arguments to pass to the function.
        initial_delay: Delay before executing the function.
        error_msg: Custom error message.
        suppress_err: Whether to suppress errors and return default value.
        timing: Whether to return the execution duration.
        timeout: Timeout for the function execution.
        default: Default value to return if an error occurs.
        error_map: Dictionary mapping exception types to error handlers.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        The result of the function call, optionally including the duration
        of execution if `timing` is True.

    Raises:
        asyncio.TimeoutError: If function execution exceeds the timeout.
        RuntimeError: If an error occurs and `suppress_err` is False.
    """
    return await CoreLib.tcall(
        func,
        *args,
        initial_delay=initial_delay,
        error_msg=error_msg,
        suppress_err=suppress_err,
        timing=timing,
        timeout=timeout,
        default=default,
        error_map=error_map,
        **kwargs,
    )


async def rcall(
    func: Callable[..., T],
    *args: Any,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = LN_UNDEFINED,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, ErrorHandler] | None = None,
    **kwargs: Any,
) -> T | tuple[T, float]:
    """
    Retry a function asynchronously with customizable options.

    Args:
        func: The function to be executed.
        *args: Positional arguments to pass to the function.
        retries: Number of retry attempts.
        initial_delay: Initial delay before the first attempt.
        delay: Delay between attempts.
        backoff_factor: Factor by which the delay increases after each attempt.
        default: Default value to return if all attempts fail.
        timeout: Timeout for each function execution.
        timing: Whether to return the execution duration.
        verbose: Whether to print retry messages.
        error_msg: Custom error message.
        error_map: Dictionary mapping exception types to error handlers.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        The result of the function call, optionally including the duration
        of execution if `timing` is True.

    Raises:
        RuntimeError: If the function fails after the specified retries.
    """
    return await CoreLib.rcall(
        func,
        *args,
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

    @deprecated  # use retry instead
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
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await rcall(func, *args, timeout=timeout, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def retry(
        retries: int = 0,
        initial_delay: float = 0,
        delay: float = 0,
        backoff_factor: float = 1,
        default: Any = LN_UNDEFINED,
        timeout: float | None = None,
        timing: bool = False,
        verbose: bool = True,
        error_msg: str | None = None,
        error_map: dict[type, Callable[[Exception], None]] | None = None,
    ) -> Callable:
        """
        Decorator to automatically retry a function call on failure.

        Args:
            retries: Number of retry attempts.
            initial_delay: Initial delay before retrying.
            delay: Delay between retries.
            backoff_factor: Factor to increase delay after each retry.
            default: Default value to return on failure.
            timeout: Timeout for each function call.
            timing: If True, logs the time taken for each call.
            verbose: If True, logs the retries.
            error_msg: Custom error message on failure.
            error_map: A map of exception types to handler functions.

        Returns:
            The decorated function.
        """
        return CoreLib.CallDecorator.retry(
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
        )

    @deprecated  # use retry instead
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
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await rcall(func, *args, default=default_value, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def throttle(period: int) -> Callable:
        """
        Decorator to limit the execution frequency of a function.

        Args:
            period: Minimum time in seconds between function calls.

        Returns:
            The decorated function.
        """
        return CoreLib.CallDecorator.throttle(period)

    @staticmethod
    def map(function: Callable[[Any], Any]) -> Callable:
        """
        Decorates an asynchronous function to apply a specified mapping function to
        each element in the list returned by the decorated function. This is
        particularly useful for post-processing the results of asynchronous operations,
        such as transforming data fetched from an API or processing items in a
        collection concurrently.

        The mapping function is applied to each input_ in the output list of the
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

        return CoreLib.CallDecorator.map(function)

    @staticmethod
    def compose(*functions: Callable[[Any], Any]) -> Callable:
        """
        Decorator to compose multiple functions, applying them in sequence.

        Args:
            functions: Functions to apply in sequence.

        Returns:
            The decorated function.
        """
        return CoreLib.CallDecorator.compose(*functions)

    @staticmethod
    def pre_post_process(
        preprocess: Callable[..., Any] = None,
        postprocess: Callable[..., Any] = None,
        preprocess_args=[],
        preprocess_kwargs={},
        postprocess_args=[],
        postprocess_kwargs={},
    ) -> Callable:
        """
        Decorator to apply pre-processing and post-processing functions.

        Args:
            preprocess: Function to apply before the main function.
            postprocess: Function to apply after the main function.
            preprocess_args: Arguments to pass to the preprocess function.
            preprocess_kwargs: Keyword arguments for the preprocess function.
            postprocess_args: Arguments to pass to the postprocess function.
            postprocess_kwargs: Keyword arguments for the postprocess function.

        Returns:
            The decorated function.
        """
        return CoreLib.CallDecorator.pre_post_process(
            preprocess=preprocess,
            postprocess=postprocess,
            preprocess_args=preprocess_args,
            preprocess_kwargs=preprocess_kwargs,
            postprocess_args=postprocess_args,
            postprocess_kwargs=postprocess_kwargs,
        )

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
            @aiocache.cached(ttl=ttl)
            async def cached_async(*args, **kwargs) -> Any:
                return await func(*args, **kwargs)

            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                return await cached_async(*args, **kwargs)

            return async_wrapper

        else:
            # Synchronous function handling
            @lru_cache(maxsize=maxsize)
            def cached_sync(*args, **kwargs) -> Any:
                return func(*args, **kwargs)

            @wraps(func)
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
                        A function that evaluates each input_ in the list. Items for which the
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

        def decorator(func: Callable[..., list[Any]]) -> Callable:
            if is_coroutine_func(func):

                @wraps(func)
                async def wrapper(*args, **kwargs) -> list[Any]:
                    values = await func(*args, **kwargs)
                    return [value for value in values if predicate(value)]

                return wrapper
            else:

                @wraps(func)
                def wrapper(*args, **kwargs) -> list[Any]:
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

        def decorator(func: Callable[..., list[Any]]) -> Callable:
            if is_coroutine_func(func):

                @wraps(func)
                async def async_wrapper(*args, **kwargs) -> Any:
                    values = await func(*args, **kwargs)
                    return reduce(function, values, initial)

                return async_wrapper
            else:

                @wraps(func)
                def sync_wrapper(*args, **kwargs) -> Any:
                    values = func(*args, **kwargs)
                    return reduce(function, values, initial)

                return sync_wrapper

        return decorator

    @deprecated  # use max_concurrenct instead
    @staticmethod
    def max_concurrency(limit: int = 5) -> Callable:
        return CoreLib.CallDecorator.max_concurrent(limit)

    @staticmethod
    def max_concurrent(limit: int = 5) -> Callable:
        """
        Decorator to limit the maximum number of concurrent executions of a function.

        Args:
            limit: Maximum number of concurrent executions.

        Returns:
            The decorated function.
        """
        return CoreLib.CallDecorator.max_concurrent(limit)

    @staticmethod
    def force_async(fn):
        pool = ThreadPoolExecutor()

        @wraps(fn)
        def wrapper(*args, **kwargs):
            future = pool.submit(fn, *args, **kwargs)
            return asyncio.wrap_future(future)  # make it awaitable

        return wrapper


def _custom_error_handler(error: Exception, error_map: dict[type, Callable]) -> None:
    # noinspection PyUnresolvedReferences
    """
    handle errors based on a given error mapping.

    Args:
            error (Exception):
                    The error to handle.
            error_map (Dict[type, Callable]):
                    A dictionary mapping error types to handler functions.

    examples:
            >>> def handle_value_error(e): print("ValueError occurred")
            >>> custom_error_handler(ValueError(), {ValueError: handle_value_error})
            ValueError occurred
    """
    if handler := error_map.get(type(error)):
        handler(error)
    else:
        logging.error(f"Unhandled error: {error}")


async def call_handler(
    func: Callable, *args, error_map: dict[type, Callable] = None, **kwargs
) -> Any:
    """
    call a function with error handling, supporting both synchronous and asynchronous
    functions.

    Args:
            func (Callable):
                    The function to call.
            *args:
                    Positional arguments to pass to the function.
            error_map (Dict[type, Callable], optional):
                    A dictionary mapping error types to handler functions.
            **kwargs:
                    Keyword arguments to pass to the function.

    Returns:
            Any: The result of the function call.

    Raises:
            Exception: Propagates any exceptions not handled by the error_map.

    examples:
            >>> async def async_add(x, y): return x + y
            >>> asyncio.run(_call_handler(async_add, 1, 2))
            3
    """
    try:
        if not is_coroutine_func(func):
            return func(*args, **kwargs)

        # Checking for a running event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # No running event loop
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(func(*args, **kwargs))

            loop.close()
            return result

        if loop.is_running():
            return await func(*args, **kwargs)

    except Exception as e:
        if error_map:
            _custom_error_handler(e, error_map)
        # else:
        #     logging.error(f"Error in call_handler: {e}")
        raise


@lru_cache(maxsize=None)
def is_coroutine_func(func: Callable) -> bool:
    """
    checks if the specified function is an asyncio coroutine function.

    this utility function is critical for asynchronous programming in Python, allowing
    developers to distinguish between synchronous and asynchronous functions.
    understanding whether a function is coroutine-enabled is essential for making
    correct asynchronous calls and for integrating synchronous functions into
    asynchronous codebases correctly.

    Args:
            func (Callable):
                    The function to check for coroutine compatibility.

    Returns:
            bool:
                    True if `func` is an asyncio coroutine function, False otherwise. this
                    determination is based on whether the function is defined with `async def`.

    examples:
            >>> async def async_func(): pass
            >>> def sync_func(): pass
            >>> is_coroutine_func(async_func)
            True
            >>> is_coroutine_func(sync_func)
            False
    """
    return asyncio.iscoroutinefunction(func)
