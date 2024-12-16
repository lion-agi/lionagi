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

import asyncio
from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, TypeVar

from ..constants import UNDEFINED
from .async_calls import rcall, ucall
from .throttle import Throttle
from .utils import force_async, is_coroutine_func

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class CallDecorator:
    """A collection of decorators to enhance function calls."""

    @staticmethod
    def retry(
        num_retries: int = 0,
        initial_delay: float = 0,
        retry_delay: float = 0,
        backoff_factor: float = 1,
        retry_default: Any = UNDEFINED,
        retry_timeout: float | None = None,
        retry_timing: bool = False,
        verbose_retry: bool = True,
        error_msg: str | None = None,
        error_map: dict[type, Callable[[Exception], None]] | None = None,
    ) -> Callable[[F], F]:
        """Decorator to automatically retry a function call on failure.

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

        def decorator(func: F) -> F:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await rcall(
                    func,
                    *args,
                    num_retries=num_retries,
                    initial_delay=initial_delay,
                    retry_delay=retry_delay,
                    backoff_factor=backoff_factor,
                    retry_default=retry_default,
                    retry_timeout=retry_timeout,
                    retry_timing=retry_timing,
                    verbose_retry=verbose_retry,
                    error_msg=error_msg,
                    error_map=error_map,
                    **kwargs,
                )

            return wrapper

        return decorator

    @staticmethod
    def throttle(period: float) -> Callable[[F], F]:
        """Decorator to limit the execution frequency of a function.

        Args:
            period: Minimum time in seconds between function calls.

        Returns:
            The decorated function.
        """

        def decorator(func: F) -> F:
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
    def max_concurrent(limit: int) -> Callable[[F], F]:
        """Decorator to limit the maximum number of concurrent executions.

        Args:
            limit: Maximum number of concurrent executions.

        Returns:
            The decorated function.
        """

        def decorator(func: F) -> F:
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
    def compose(*functions: Callable[[T], T]) -> Callable[[F], F]:
        """Decorator to compose multiple functions, applying in sequence.

        Args:
            functions: Functions to apply in sequence.

        Returns:
            The decorated function.
        """

        def decorator(func: F) -> F:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                value = await ucall(func, *args, **kwargs)
                for function in functions:
                    try:
                        value = await ucall(function, value)
                    except Exception as e:
                        raise ValueError(
                            f"Error in function {function.__name__}: {e}"
                        )
                return value

            return async_wrapper

        return decorator

    @staticmethod
    def pre_post_process(
        preprocess: Callable[..., Any] | None = None,
        postprocess: Callable[..., Any] | None = None,
        preprocess_args: Sequence[Any] = (),
        preprocess_kwargs: dict[str, Any] = {},
        postprocess_args: Sequence[Any] = (),
        postprocess_kwargs: dict[str, Any] = {},
    ) -> Callable[[F], F]:
        """Decorator to apply pre-processing and post-processing functions.

        Args:
            preprocess: Function to apply before the main function.
            postprocess: Function to apply after the main function.
            preprocess_args: Arguments for the preprocess function.
            preprocess_kwargs: Keyword arguments for preprocess function.
            postprocess_args: Arguments for the postprocess function.
            postprocess_kwargs: Keyword arguments for postprocess function.

        Returns:
            The decorated function.
        """

        def decorator(func: F) -> F:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                preprocessed_args = (
                    [
                        await ucall(
                            preprocess,
                            arg,
                            *preprocess_args,
                            **preprocess_kwargs,
                        )
                        for arg in args
                    ]
                    if preprocess
                    else args
                )
                preprocessed_kwargs = (
                    {
                        k: await ucall(
                            preprocess,
                            v,
                            *preprocess_args,
                            **preprocess_kwargs,
                        )
                        for k, v in kwargs.items()
                    }
                    if preprocess
                    else kwargs
                )
                result = await ucall(
                    func, *preprocessed_args, **preprocessed_kwargs
                )

                return (
                    await ucall(
                        postprocess,
                        result,
                        *postprocess_args,
                        **postprocess_kwargs,
                    )
                    if postprocess
                    else result
                )

            return async_wrapper

        return decorator

    @staticmethod
    def map(function: Callable[[Any], Any]) -> Callable:
        """Decorator to map a function over async function results.

        Applies a mapping function to each element in the list returned
        by the decorated function. Useful for post-processing results of
        asynchronous operations, such as transforming data fetched from
        an API or processing items in a collection concurrently.

        Args:
            function: Mapping function to apply to each element.

        Returns:
            Decorated async function with transformed results.

        Examples:
            >>> @CallDecorator.map(lambda x: x.upper())
            ... async def get_names():
            ...     return ["alice", "bob", "charlie"]
            ... # `get_names` now returns ["ALICE", "BOB", "CHARLIE"]
        """

        def decorator(func: Callable[..., list[Any]]) -> Callable:
            if is_coroutine_func(func):

                @wraps(func)
                async def async_wrapper(*args, **kwargs) -> list[Any]:
                    values = await func(*args, **kwargs)
                    return [function(value) for value in values]

                return async_wrapper
            else:

                @wraps(func)
                def sync_wrapper(*args, **kwargs) -> list[Any]:
                    values = func(*args, **kwargs)
                    return [function(value) for value in values]

                return sync_wrapper

        return decorator
