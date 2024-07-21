from __future__ import annotations

import asyncio
from collections.abc import Mapping, Callable, Coroutine
from functools import lru_cache
from typing import Any
import logging
import aiocache
from typing_extensions import deprecated


@deprecated
class AsyncUtil:

    @deprecated  # internal testing methods, will be removed in v1.0.0
    @staticmethod
    async def _call_handler(
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
            if not AsyncUtil.is_coroutine_func(func):
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
                AsyncUtil._custom_error_handler(e, error_map)
            else:
                logging.error(f"Error in call_handler: {e}")
            raise

    @deprecated  # internal testing methods, will be removed in v1.0.0, use functools.lru_cache instead
    @staticmethod
    @lru_cache(maxsize=None)
    def is_coroutine_func(func: Callable[..., Any]) -> bool:
        """
        Checks whether a function is an asyncio coroutine function.

        Args:
                func: The function to check.

        Returns:
                True if the function is a coroutine function, False otherwise.
        """
        return asyncio.iscoroutinefunction(func)

    @deprecated  # internal methods, will be removed in v1.0.0 with no replacement
    @staticmethod
    def _custom_error_handler(
        error: Exception, error_map: Mapping[type, Callable]
    ) -> None:
        # noinspection PyUnresolvedReferences
        """
        handle errors based on a given error mapping.

        Args:
                error (Exception):
                        The error to handle.
                error_map (Mapping[type, Callable]):
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

    @deprecated  # internal methods, will be removed in v1.0.0, use ln_func_call.ucall instead
    @staticmethod
    async def handle_async_sync(
        func: Callable[..., Any], *args, error_map=None, **kwargs
    ) -> Any:
        """
        Executes a function, automatically handling synchronous and asynchronous functions.

        Args:
                func: The function to execute.
                *args: Positional arguments for the function.
                **kwargs: Keyword arguments for the function.

        Returns:
                The result of the function execution.
        """

        try:
            if not AsyncUtil.is_coroutine_func(func):
                return func(*args, **kwargs)

            try:
                loop = asyncio.get_event_loop()

                return (
                    await func(*args, **kwargs)
                    if loop.is_running()
                    else await asyncio.run(func(*args, **kwargs))
                )
            except RuntimeError:
                return asyncio.run(func(*args, **kwargs))

        except Exception as e:
            if error_map:
                AsyncUtil._custom_error_handler(e, error_map)
            else:
                logging.error(f"Error in call_handler: {e}")
            raise

    @deprecated  # internal methods, will be removed in v1.0.0, use asyncio.gather instead
    @staticmethod
    async def execute_tasks(*tasks):
        if isinstance(tasks[0], (asyncio.Future, Coroutine)):
            return await asyncio.gather(*tasks)
        else:
            return tasks

    @deprecated  # internal methods, will be removed in v1.0.0, use asyncio.sleep instead
    @staticmethod
    async def sleep(seconds):
        await asyncio.sleep(seconds)

    @deprecated  # internal methods, will be removed in v1.0.0, use asyncio.Task instead
    @classmethod
    def Task(cls):
        return asyncio.Task

    @deprecated  # internal methods, will be removed in v1.0.0, use asyncio.Event instead
    @classmethod
    def Event(cls):
        return asyncio.Event

    @deprecated  # internal methods, will be removed in v1.0.0, use asyncio.Lock instead
    @classmethod
    def Lock(cls):
        return asyncio.Lock

    @deprecated  # internal methods, will be removed in v1.0.0, use asyncio.wrap_future instead
    @staticmethod
    def wrap_future(future_):
        return asyncio.wrap_future(future_)

    @deprecated  # internal methods, will be removed in v1.0.0, use asyncio.Semaphore instead
    @staticmethod
    def semaphore(limit):
        return asyncio.Semaphore(limit)

    @deprecated  # moved into funcall.CallDecorator.cache, will be removed in v1.0.0
    @staticmethod
    def cached(*args, **kwargs):
        return aiocache.cached(*args, **kwargs)

    @deprecated  # use asyncio.Task instead, will be removed in v1.0.0
    @staticmethod
    def create_event(*args, **kwargs):
        return asyncio.Event(*args, **kwargs)

    @deprecated  # use asyncio.create_task instead, will be removed in v1.0.0
    @staticmethod
    def create_task(*args, obj=True, **kwargs):
        if obj:
            return asyncio.Task(*args, **kwargs)
        else:
            return asyncio.create_task(*args, **kwargs)

    @deprecated  # use asyncio.Lock instead, will be removed in v1.0.0
    @staticmethod
    def create_lock(*args, **kwargs):
        return asyncio.Lock(*args, **kwargs)
