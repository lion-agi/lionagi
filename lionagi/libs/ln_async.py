from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Coroutine, Mapping
from functools import lru_cache
from typing import Any

import aiocache
import aiohttp


class AsyncUtil:

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

    @staticmethod
    async def execute_tasks(*tasks):
        if isinstance(tasks[0], (asyncio.Future, Coroutine)):
            return await asyncio.gather(*tasks)
        else:
            return tasks

    @staticmethod
    async def sleep(seconds):
        await asyncio.sleep(seconds)

    # @staticmethod
    # async def execute_timeout(coro, timeout):
    #     return

    # @classmethod
    # def TimeoutError(cls):
    #     return asyncio.TimeoutError

    # @classmethod
    # def CancelledError(cls):
    #     return asyncio.CancelledError

    @classmethod
    def Task(cls):
        return asyncio.Task

    @classmethod
    def Event(cls):
        return asyncio.Event

    @classmethod
    def Lock(cls):
        return asyncio.Lock

    @staticmethod
    def wrap_future(future_):
        return asyncio.wrap_future(future_)

    @staticmethod
    def semaphore(limit):
        return asyncio.Semaphore(limit)

    @staticmethod
    def cached(*args, **kwargs):
        return aiocache.cached(*args, **kwargs)

    @staticmethod
    def create_event(*args, **kwargs):
        return asyncio.Event(*args, **kwargs)

    @staticmethod
    def create_task(*args, obj=True, **kwargs):
        if obj:
            return asyncio.Task(*args, **kwargs)
        else:
            return asyncio.create_task(*args, **kwargs)

    @staticmethod
    def create_lock(*args, **kwargs):
        return asyncio.Lock(*args, **kwargs)

    # @classmethod  # def HttpClientSession(cls):  #     return aiohttp.ClientSession

    # @classmethod  # def HttpClientError(cls):  #     return aiohttp.ClientError
