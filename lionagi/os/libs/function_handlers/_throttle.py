"""
This module provides a throttling mechanism for function calls.

The Throttle class can be used to ensure that a decorated function, either
synchronous or asynchronous, is only called once per specified period. It
delays subsequent calls within this period to enforce this constraint.

Classes:
- Throttle: Provides the throttling mechanism for function calls.
"""

import time
import asyncio
import functools
from typing import Any, Callable
from lionagi.os.libs.sys_util import get_now


class Throttle:
    """
    A class that provides a throttling mechanism for function calls.

    When used as a decorator, it ensures that the decorated function can only
    be called once per specified period. Subsequent calls within this period
    are delayed to enforce this constraint.

    Attributes:
        period (int): The minimum time period (in seconds) between successive
            calls.

    Methods:
        __call__: Decorates a synchronous function with throttling.
        __call_async__: Decorates an asynchronous function with throttling.
    """

    def __init__(self, period: int) -> None:
        """
        Initializes a new instance of Throttle.

        Args:
            period (int): The minimum time period (in seconds) between
                successive calls.
        """
        self.period = period
        self.last_called = 0

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorates a synchronous function with the throttling mechanism.

        Args:
            func (Callable[..., Any]): The synchronous function to be
                throttled.

        Returns:
            Callable[..., Any]: The throttled synchronous function.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = get_now(datetime_=False) - self.last_called
            if elapsed < self.period:
                time.sleep(self.period - elapsed)
            self.last_called = get_now(datetime_=False)
            return func(*args, **kwargs)

        return wrapper

    def __call_async__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorates an asynchronous function with the throttling mechanism.

        Args:
            func (Callable[..., Any]): The asynchronous function to be
                throttled.

        Returns:
            Callable[..., Any]: The throttled asynchronous function.
        """

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            elapsed = get_now(datetime_=False) - self.last_called
            if elapsed < self.period:
                await asyncio.sleep(self.period - elapsed)
            self.last_called = get_now(datetime_=False)
            return await func(*args, **kwargs)

        return wrapper
