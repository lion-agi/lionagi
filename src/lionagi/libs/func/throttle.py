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
import functools
import time
from collections.abc import Callable
from typing import Any, TypeVar

from ..utils import time as _t
from .utils import force_async, is_coroutine_func

T = TypeVar("T")


class Throttle:
    """
    Provide a throttling mechanism for function calls.

    When used as a decorator, it ensures that the decorated function can only
    be called once per specified period. Subsequent calls within this period
    are delayed to enforce this constraint.

    Attributes:
        period: The minimum time period (in seconds) between successive calls.
    """

    def __init__(self, period: float) -> None:
        """
        Initialize a new instance of Throttle.

        Args:
            period: The minimum time period (in seconds) between
                successive calls.
        """
        self.period = period
        self.last_called = 0

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorate a synchronous function with the throttling mechanism.

        Args:
            func: The synchronous function to be throttled.

        Returns:
            The throttled synchronous function.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = _t() - self.last_called
            if elapsed < self.period:
                time.sleep(self.period - elapsed)
            self.last_called = _t()
            return func(*args, **kwargs)

        return wrapper

    def __call_async__(
        self, func: Callable[..., Callable[..., T]]
    ) -> Callable[..., Callable[..., T]]:
        """
        Decorate an asynchronous function with the throttling mechanism.

        Args:
            func: The asynchronous function to be throttled.

        Returns:
            The throttled asynchronous function.
        """

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            elapsed = _t() - self.last_called
            if elapsed < self.period:
                await asyncio.sleep(self.period - elapsed)
            self.last_called = _t()
            return await func(*args, **kwargs)

        return wrapper


def throttle(
    func: Callable[..., T], period: float
) -> Callable[..., Callable[..., T]]:
    """
    Throttle function execution to limit the rate of calls.

    Args:
        func: The function to throttle.
        period: The minimum time interval between consecutive calls.

    Returns:
        The throttled function.
    """
    if not is_coroutine_func(func):
        func = force_async(func)
    throttle_instance = Throttle(period)

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        await throttle_instance(func)(*args, **kwargs)
        return await func(*args, **kwargs)

    return wrapper
