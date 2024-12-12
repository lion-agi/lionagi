# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
import asyncio
import copy as _copy
import logging
from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache, wraps
from typing import Any, Literal, TypeVar

T = TypeVar("T")


class UndefinedType:
    def __init__(self) -> None:
        self.undefined = True

    def __bool__(self) -> Literal[False]:
        return False

    def __deepcopy__(self, memo):
        # Ensure UNDEFINED is universal
        return self

    def __repr__(self) -> Literal["UNDEFINED"]:
        return "UNDEFINED"

    __slots__ = ["undefined"]


UNDEFINED = UndefinedType()


def time(
    *,
    tz: timezone = timezone.utc,
    type_: Literal["timestamp", "datetime", "iso", "custom"] = "timestamp",
    sep: str | None = "T",
    timespec: str | None = "auto",
    custom_strftime: str | None = None,
) -> float | str | datetime:
    """Get current time in specified format.

    Args:
        tz: Target timezone (default: UTC)
        type_: Output format:
            - "timestamp": Unix timestamp
            - "datetime": datetime object
            - "iso": ISO format string
            - "custom": Custom format string
        sep: ISO format separator
        timespec: ISO format timespec
        custom_format: strftime format string for custom type
        custom_sep: Custom separator for custom format

    Returns:
        Current time in requested format

    Raises:
        ValueError: Invalid type_ or missing custom_format
    """
    now = datetime.now(tz=tz)

    match type_:
        case "iso":
            return now.isoformat(sep=sep, timespec=timespec)
        case "timestamp":
            return now.timestamp()
        case "datetime":
            return now
        case "custom":
            if not custom_strftime:
                raise ValueError(
                    "custom_format must be provided when type_='custom'"
                )
            return now.strftime(custom_strftime)
        case _:
            raise ValueError(
                f"Invalid value <{type_}> for `type_`, must be"
                " one of 'timestamp', 'datetime', 'iso', or 'custom'."
            )


def copy(obj: T, /, *, deep: bool = True, num: int = 1) -> T | list[T]:
    if num < 1:
        raise ValueError("Number of copies must be at least 1")

    copy_func = _copy.deepcopy if deep else _copy.copy
    return [copy_func(obj) for _ in range(num)] if num > 1 else copy_func(obj)


class ItemError(Exception):
    """Base for framework item errors."""

    def __init__(
        self, message: str = "Item error.", item_id: str | None = None
    ):
        self.item_id = item_id
        item_info = f" Item ID: {item_id}" if item_id else ""
        super().__init__(f"{message}{item_info}")


class IDError(ItemError):
    """Raised when item lacks valid Lion ID."""

    def __init__(
        self,
        message: str = "Item must contain a Lion ID.",
        item_id: str | None = None,
    ):
        super().__init__(message, item_id)


class ItemNotFoundError(ItemError):
    """Raised when item cannot be found."""

    def __init__(
        self, message: str = "Item not found.", item_id: str | None = None
    ):
        super().__init__(message, item_id)


class ItemExistsError(ItemError):
    """Raised when item already exists."""

    def __init__(
        self, message: str = "Item already exists.", item_id: str | None = None
    ):
        super().__init__(message, item_id)


def is_same_dtype(
    input_: list | dict, dtype: type | None = None, return_dtype: bool = False
) -> bool | tuple[bool, type]:
    """Check if all elements in input have the same data type."""
    if not input_:
        return True if not return_dtype else (True, None)

    iterable = input_.values() if isinstance(input_, Mapping) else input_
    first_element_type = type(next(iter(iterable), None))

    dtype = dtype or first_element_type
    result = all(isinstance(element, dtype) for element in iterable)
    return (result, dtype) if return_dtype else result


def force_async(fn: Callable[..., T]) -> Callable[..., Callable[..., T]]:
    """
    Convert a synchronous function to an asynchronous function
    using a thread pool.

    Args:
        fn: The synchronous function to convert.

    Returns:
        The asynchronous version of the function.
    """
    pool = ThreadPoolExecutor()

    @wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # Make it awaitable

    return wrapper


@lru_cache(maxsize=None)
def is_coroutine_func(func: Callable[..., Any]) -> bool:
    """
    Check if a function is a coroutine function.

    Args:
        func: The function to check.

    Returns:
        True if the function is a coroutine function, False otherwise.
    """
    return asyncio.iscoroutinefunction(func)


def max_concurrent(
    func: Callable[..., T], limit: int
) -> Callable[..., Callable[..., T]]:
    """
    Limit the concurrency of function execution using a semaphore.

    Args:
        func: The function to limit concurrency for.
        limit: The maximum number of concurrent executions.

    Returns:
        The function wrapped with concurrency control.
    """
    if not is_coroutine_func(func):
        func = force_async(func)
    semaphore = asyncio.Semaphore(limit)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with semaphore:
            return await func(*args, **kwargs)

    return wrapper


async def custom_error_handler(
    error: Exception, error_map: dict[type, Callable[[Exception], None]]
) -> None:
    for error_type, handler in error_map.items():
        if isinstance(error, error_type):
            if is_coroutine_func(handler):
                return await handler(error)
            return handler(error)
    logging.error(f"Unhandled error: {error}")
