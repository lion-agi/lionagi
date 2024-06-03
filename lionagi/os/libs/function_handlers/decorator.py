import asyncio
from typing import Any, Callable, List, Dict, Optional
from functools import wraps, lru_cache
from aiocache import cached

from lionagi.os.libs.function_handlers._throttle import Throttle
from lionagi.os.libs.function_handlers._util import is_coroutine_func, force_async
from lionagi.os.libs.function_handlers._ucall import ucall
from lionagi.os.libs.function_handlers._rcall import rcall


class CallDecorator:
    """A collection of decorators to enhance function calls with features
    like retries, throttling, concurrency limits, composition, and caching.
    """

    @staticmethod
    def retry(
        retries: int = 0,
        initial_delay: float = 0,
        delay: float = 0,
        backoff_factor: float = 1,
        default: Any = ...,
        timeout: Optional[float] = None,
        timing: bool = False,
        verbose: bool = True,
        error_msg: Optional[str] = None,
        error_map: Optional[Dict[type, Callable[[Exception], None]]] = None,
    ) -> Callable:
        """Decorator to automatically retry a function call on failure.

        Args:
            retries (int): Number of retry attempts. Defaults to 0.
            initial_delay (float): Initial delay before retrying. Defaults to 0.
            delay (float): Delay between retries. Defaults to 0.
            backoff_factor (float): Factor to increase delay after each retry.
                                    Defaults to 1.
            default (Any): Default value to return on failure.
            timeout (Optional[float]): Timeout for each function call. Defaults to None.
            timing (bool): If True, logs the time taken for each call. Defaults to False.
            verbose (bool): If True, logs the retries. Defaults to True.
            error_msg (Optional[str]): Custom error message on failure. Defaults to None.
            error_map (Optional[Dict[type, Callable[[Exception], None]]]):
                      A map of exception types to handler functions.

        Returns:
            Callable: The decorated function.
        """

        def decorator(func: Callable[..., Any]) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await rcall(
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

            return wrapper

        return decorator

    @staticmethod
    def throttle(period: float) -> Callable:
        """Decorator to limit the execution frequency of a function.

        Args:
            period (float): Minimum time in seconds between function calls.

        Returns:
            Callable: The decorated function.
        """

        def decorator(func: Callable) -> Callable:
            if not is_coroutine_func(func):
                func = force_async(func)
            throttle_instance = Throttle(period)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                await throttle_instance(func)(*args, **kwargs)
                return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def max_concurrent(limit: int) -> Callable:
        """Decorator to limit the maximum number of concurrent executions.

        Args:
            limit (int): Maximum number of concurrent executions.

        Returns:
            Callable: The decorated function.
        """

        def decorator(func: Callable) -> Callable:
            if not is_coroutine_func(func):
                func = force_async(func)
            semaphore = asyncio.Semaphore(limit)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                async with semaphore:
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def compose(*functions: Callable[[Any], Any]) -> Callable:
        """Decorator to compose multiple functions, applying them in sequence.

        Args:
            functions (Callable[[Any], Any]): Functions to apply in sequence.

        Returns:
            Callable: The decorated function.
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                value = await ucall(func, *args, **kwargs)
                for function in functions:
                    try:
                        value = await ucall(function, value)
                    except Exception as e:
                        raise ValueError(f"Error in function {function.__name__}: {e}")
                return value

            return async_wrapper

        return decorator

    @staticmethod
    def pre_post_process(
        preprocess: Callable[..., Any] = None,
        postprocess: Callable[..., Any] = None,
        preprocess_args: List = [],
        preprocess_kwargs: Dict = {},
        postprocess_args: List = [],
        postprocess_kwargs: Dict = {},
    ) -> Callable:
        """Decorator to apply pre-processing and post-processing functions.

        Args:
            preprocess (Callable[..., Any]): Function to apply before the main function.
            postprocess (Callable[..., Any]): Function to apply after the main function.
            preprocess_args (List): Arguments to pass to the preprocess function.
            preprocess_kwargs (Dict): Keyword arguments to pass to the preprocess function.
            postprocess_args (List): Arguments to pass to the postprocess function.
            postprocess_kwargs (Dict): Keyword arguments to pass to the postprocess function.

        Returns:
            Callable: The decorated function.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:

            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                preprocessed_args = (
                    [
                        await ucall(
                            preprocess, arg, *preprocess_args, **preprocess_kwargs
                        )
                        for arg in args
                    ]
                    if preprocess
                    else args
                )
                preprocessed_kwargs = (
                    {
                        k: await ucall(
                            preprocess, v, *preprocess_args, **preprocess_kwargs
                        )
                        for k, v in kwargs.items()
                    }
                    if preprocess
                    else kwargs
                )
                result = await ucall(func, *preprocessed_args, **preprocessed_kwargs)

                return (
                    await ucall(
                        postprocess, result, *postprocess_args, **postprocess_kwargs
                    )
                    if postprocess
                    else result
                )

            return async_wrapper

        return decorator

    @staticmethod
    def cache(ttl: int = 600, maxsize: int = None) -> Callable:
        """Decorator to cache the result of a function call.

        Args:
            ttl (int): Time-to-live for the cache in seconds. Defaults to 600.
            maxsize (int): Maximum size of the cache. Defaults to None.

        Returns:
            Callable: The decorated function.
        """

        def decorator(func: Callable) -> Callable:
            if is_coroutine_func(func):

                @cached(ttl=ttl)
                async def cached_async(*args, **kwargs) -> Any:
                    return await func(*args, **kwargs)

                @wraps(func)
                async def async_wrapper(*args, **kwargs) -> Any:
                    return await cached_async(*args, **kwargs)

                return async_wrapper
            else:

                @lru_cache(maxsize=maxsize)
                def cached_sync(*args, **kwargs) -> Any:
                    return func(*args, **kwargs)

                @wraps(func)
                def sync_wrapper(*args, **kwargs) -> Any:
                    return cached_sync(*args, **kwargs)

                return sync_wrapper

        return decorator
