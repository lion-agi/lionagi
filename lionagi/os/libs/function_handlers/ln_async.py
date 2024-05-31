from __future__ import annotations

import asyncio
from collections.abc import Mapping, Callable, Coroutine
from functools import lru_cache
from typing import Any
import logging
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
