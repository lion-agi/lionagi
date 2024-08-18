from collections.abc import Callable, Sequence
from typing import Any
from functools import wraps, lru_cache, reduce

from lion_core.setting import LN_UNDEFINED
from lion_core.libs import CallDecorator as CoreCallDecorator
from lion_core.libs.function_handlers._util import force_async, is_coroutine_func


class CallDecorator:

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
        error_map: dict = None,
    ):
        return CoreCallDecorator.retry(
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

    @staticmethod
    def default(default: Any):
        return CoreCallDecorator.retry(default=default)

    @staticmethod
    def timeout(timeout: float):
        return CoreCallDecorator.retry(timeout=timeout)

    @staticmethod
    def throttle(period: float):
        return CoreCallDecorator.throttle(period=period)

    @staticmethod
    def max_concurrent(limit: int):
        return CoreCallDecorator.max_concurrent(limit=limit)

    @staticmethod
    def compose(*funcs):
        return CoreCallDecorator.compose(*funcs)

    @staticmethod
    def pre_post_process(
        preprocess: Callable[..., Any] | None = None,
        postprocess: Callable[..., Any] | None = None,
        preprocess_args: Sequence[Any] = (),
        preprocess_kwargs: dict[str, Any] = {},
        postprocess_args: Sequence[Any] = (),
        postprocess_kwargs: dict[str, Any] = {},
    ):
        return CoreCallDecorator.pre_post_process(
            preprocess=preprocess,
            postprocess=postprocess,
            preprocess_args=preprocess_args,
            preprocess_kwargs=preprocess_kwargs,
            postprocess_args=postprocess_args,
            postprocess_kwargs=postprocess_kwargs,
        )

    @staticmethod
    def map(function):
        return CoreCallDecorator.map(function)

    @staticmethod
    def cache(func: Callable, ttl=600, maxsize=None) -> Callable:

        if is_coroutine_func(func):
            from aiocache import cached

            # Asynchronous function handling
            @cached(ttl=ttl)
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

    @staticmethod
    def force_async(fn):
        return force_async(fn)


__all__ = ["CallDecorator"]
