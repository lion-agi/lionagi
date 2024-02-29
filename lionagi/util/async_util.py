from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import Any, Callable, Dict
import logging


class AsyncUtil:
    
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
    def _custom_error_handler(error: Exception, error_map: Dict[type, Callable]) -> None:
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
        handler = error_map.get(type(error))
        if handler:
            handler(error)
        else:
            logging.error(f"Unhandled error: {error}")


    @staticmethod
    async def handle_async_sync(func: Callable[..., Any], *args, error_map=None, **kwargs) -> Any:
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
            if AsyncUtil.is_coroutine_func(func):
                
                try:
                    loop = asyncio.get_event_loop()
                    
                    if loop.is_running():
                        return await func(*args, **kwargs)
                    else:
                        return await asyncio.run(func(*args, **kwargs))

                except RuntimeError:
                    return asyncio.run(func(*args, **kwargs))

            else:
                return func(*args, **kwargs)
        
        except Exception as e:
            if error_map:
                AsyncUtil._custom_error_handler(e, error_map)
            else:
                logging.error(f"Error in call_handler: {e}")
            raise
            
    @staticmethod
    async def execute_tasks(*tasks):
        return await asyncio.gather(*tasks)
    
    @staticmethod
    async def sleep(seconds):
        await asyncio.sleep(seconds)

    @staticmethod
    async def execute_timeout(coro, timeout):
        return await asyncio.wait_for(coro, timeout)

    @property
    def TimeoutError(self):
        return asyncio.TimeoutError
    
    @staticmethod
    def wrap_future(future_):
        return asyncio.wrap_future(future_)
    
    @staticmethod
    def semaphore(limit):
        return asyncio.Semaphore(limit)
    