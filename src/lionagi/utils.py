# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
import ast
import asyncio
import copy as _copy
import importlib.util
import logging
import os
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from enum import Enum
from functools import lru_cache, wraps
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal, TypeVar, overload

from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType

__all__ = (
    "UNDEFINED",
    "UndefinedType",
    "ItemError",
    "IDError",
    "ItemNotFoundError",
    "ItemExistsError",
    "is_same_dtype",
    "force_async",
    "max_concurrent",
    "custom_error_handler",
    "to_list",
    "ucall",
    "alcall",
    "time",
    "copy",
    "get_file_classes",
    "get_class_file_registry",
    "get_class_objects",
    "unique_hash",
    "create_path",
)


T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


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


@overload
def to_list(
    input_: None | UndefinedType | PydanticUndefinedType, /
) -> list: ...


@overload
def to_list(
    input_: str | bytes | bytearray, /, use_values: bool = False
) -> list[str | int]: ...


@overload
def to_list(input_: Mapping, /, use_values: bool = False) -> list[Any]: ...


@overload
def to_list(
    input_: Any,
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
) -> list: ...


def to_list(
    input_: Any,
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
    use_values: bool = False,
) -> list:
    """Convert various input types to a list.

    Handles different input types and converts them to a list, with options
    for flattening nested structures and removing None values.

    Args:
        input_: The input to be converted to a list.
        flatten: If True, flattens nested list structures.
        dropna: If True, removes None values from the result.
        unique: If True, returns only unique values (requires flatten=True).
        use_values: If True, uses .values() for dict-like inputs.

    Returns:
        A list derived from the input, processed as specified.

    Raises:
        ValueError: If unique=True and flatten=False.

    Examples:
        >>> to_list(1)
        [1]
        >>> to_list([1, [2, 3]], flatten=True)
        [1, 2, 3]
        >>> to_list([1, None, 2], dropna=True)
        [1, 2]
        >>> to_list({'a': 1, 'b': 2}, use_values=True)
        [1, 2]
    """
    lst_ = _to_list_type(input_, use_values=use_values)

    if any((flatten, dropna)):
        lst_ = _process_list(
            lst=lst_,
            flatten=flatten,
            dropna=dropna,
        )

    if unique:
        out_ = []
        for i in lst_:
            if i not in out_:
                out_.append(i)
        return out_

    return lst_


def _undefined_to_list(
    input_: None | UndefinedType | PydanticUndefinedType, /
) -> list:
    return []


def _str_to_list(
    input_: str | bytes | bytearray, /, use_values: bool = False
) -> list[str | int]:
    if use_values:
        return list(input_)
    return [input_]


def _enum_to_list(
    input_: type[Enum], /, use_values: bool = False
) -> list[Any]:
    if use_values:
        return [i.value for i in input_.__members__.values()]
    return list(input_)


def _dict_to_list(input_: Mapping, /, use_values: bool = False) -> list[Any]:
    if use_values:
        return list(input_.values())
    return [input_]


def _to_list_type(input_: Any, /, use_values: bool = False) -> Any | None:

    if isinstance(input_, BaseModel):
        return [input_]

    if use_values and hasattr(input_, "values"):
        return list(input_.values())

    if isinstance(input_, list):
        return input_

    if isinstance(input_, type(None) | UndefinedType | PydanticUndefinedType):
        return _undefined_to_list(input_)

    if isinstance(input_, type) and issubclass(input_, Enum):
        return _enum_to_list(input_, use_values=use_values)

    if isinstance(input_, str | bytes | bytearray):
        return _str_to_list(input_, use_values=use_values)

    if isinstance(input_, dict):
        return _dict_to_list(input_, use_values=use_values)

    if isinstance(input_, Iterable):
        return list(input_)

    return [input_]


def _process_list(lst: list[Any], flatten: bool, dropna: bool) -> list[Any]:
    """Process a list by optionally flattening and removing None values.

    Args:
        lst: The list to process.
        flatten: If True, flattens nested list structures.
        dropna: If True, removes None values.

    Returns:
        The processed list.
    """
    result = []
    for item in lst:
        if isinstance(item, Iterable) and not isinstance(
            item, (str, bytes, bytearray, Mapping, BaseModel)
        ):
            if flatten:
                result.extend(
                    _process_list(
                        lst=list(item),
                        flatten=flatten,
                        dropna=dropna,
                    )
                )
            else:
                result.append(
                    _process_list(
                        lst=list(item),
                        flatten=flatten,
                        dropna=dropna,
                    )
                )
        elif not dropna or item not in [None, UNDEFINED]:
            result.append(item)

    return result


async def ucall(
    func: Callable[..., T],
    /,
    *args: Any,
    error_map: dict[type, Callable[[Exception], None]] | None = None,
    **kwargs: Any,
) -> T:
    """Execute a function asynchronously with error handling.

    Ensures asynchronous execution of both coroutine and regular functions,
    managing event loops and applying custom error handling.

    Args:
        func: The function to be executed (coroutine or regular).
        *args: Positional arguments for the function.
        error_map: Dict mapping exception types to error handlers.
        **kwargs: Keyword arguments for the function.

    Returns:
        T: The result of the function call.

    Raises:
        Exception: Any unhandled exception from the function execution.

    Examples:
        >>> async def example_func(x):
        ...     return x * 2
        >>> await ucall(example_func, 5)
        10
        >>> await ucall(lambda x: x + 1, 5)  # Non-coroutine function
        6

    Note:
        - Automatically wraps non-coroutine functions for async execution.
        - Manages event loop creation and closure when necessary.
        - Applies custom error handling based on the provided error_map.
    """
    try:
        if not is_coroutine_func(func):
            return func(*args, **kwargs)

        # Checking for a running event loop
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                return await func(*args, **kwargs)
            else:
                return await asyncio.run(func(*args, **kwargs))

        except RuntimeError:  # No running event loop
            loop = asyncio.new_event_loop()
            result = await func(*args, **kwargs)
            loop.close()
            return result

    except Exception as e:
        if error_map:

            return await custom_error_handler(e, error_map)
        raise e


async def alcall(
    input_: list[Any],
    func: Callable[..., T],
    /,
    num_retries: int = 0,
    delay: float = 0,
    retry_delay: float = 0,
    backoff_factor: float = 1,
    default: Any = UNDEFINED,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, Callable[[Exception], None]] | None = None,
    max_concurrent: int | None = None,
    throttle_period: float | None = None,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
    **kwargs: Any,
) -> list[T] | list[tuple[T, float]]:
    """Apply a function to each element of a list asynchronously with options.

    Args:
        input_: List of inputs to be processed.
        func: Async or sync function to apply to each input element.
        num_retries: Number of retry attempts for each function call.
        delay: Initial delay before starting execution (seconds).
        retry_delay: Delay between retry attempts (seconds).
        backoff_factor: Factor by which delay increases after each attempt.
        retry_default: Default value to return if all attempts fail.
        retry_timeout: Timeout for each function execution (seconds).
        retry_timing: If True, return execution duration for each call.
        verbose: If True, print retry messages.
        error_msg: Custom error message prefix for exceptions.
        error_map: Dict mapping exception types to error handlers.
        max_concurrent: Maximum number of concurrent executions.
        throttle_period: Minimum time between function executions (seconds).
        flatten: If True, flatten the resulting list.
        dropna: If True, remove None values from the result.
        **kwargs: Additional keyword arguments passed to func.

    Returns:
        list[T] | list[tuple[T, float]]: List of results, optionally with
        execution times if retry_timing is True.

    Raises:
        asyncio.TimeoutError: If execution exceeds retry_timeout.
        Exception: Any exception raised by func if not handled by error_map.

    Examples:
        >>> async def square(x):
        ...     return x * x
        >>> await alcall([1, 2, 3], square)
        [1, 4, 9]
        >>> await alcall([1, 2, 3], square, retry_timing=True)
        [(1, 0.001), (4, 0.001), (9, 0.001)]

    Note:
        - Uses semaphores for concurrency control if max_concurrent is set.
        - Supports both synchronous and asynchronous functions for `func`.
        - Results are returned in the original input order.
    """
    if delay:
        await asyncio.sleep(delay)

    semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
    throttle_delay = throttle_period if throttle_period else 0

    async def _task(i: Any, index: int) -> Any:
        if semaphore:
            async with semaphore:
                return await _execute_task(i, index)
        else:
            return await _execute_task(i, index)

    async def _execute_task(i: Any, index: int) -> Any:
        attempts = 0
        current_delay = retry_delay
        while True:
            try:
                if timing:
                    start_time = asyncio.get_event_loop().time()
                    result = await asyncio.wait_for(
                        ucall(func, i, **kwargs), timeout
                    )
                    end_time = asyncio.get_event_loop().time()
                    return index, result, end_time - start_time
                else:
                    result = await asyncio.wait_for(
                        ucall(func, i, **kwargs), timeout
                    )
                    return index, result
            except TimeoutError as e:
                raise TimeoutError(
                    f"{error_msg or ''} Timeout {timeout} seconds " "exceeded"
                ) from e
            except Exception as e:
                if error_map and type(e) in error_map:
                    handler = error_map[type(e)]
                    if asyncio.iscoroutinefunction(handler):
                        return index, await handler(e)
                    else:
                        return index, handler(e)
                attempts += 1
                if attempts <= num_retries:
                    if verbose:
                        print(
                            f"Attempt {attempts}/{num_retries} failed: {e}"
                            ", retrying..."
                        )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
                else:
                    if default is not UNDEFINED:
                        return index, default
                    raise e

    tasks = [_task(i, index) for index, i in enumerate(input_)]
    results = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        await asyncio.sleep(throttle_delay)

    results.sort(
        key=lambda x: x[0]
    )  # Sort results based on the original index

    if timing:
        if dropna:
            return [
                (result[1], result[2])
                for result in results
                if result[1] is not None
            ]
        else:
            return [(result[1], result[2]) for result in results]
    else:
        return to_list(
            [result[1] for result in results],
            flatten=flatten,
            dropna=dropna,
            unique=unique,
        )


def get_file_classes(file_path):
    with open(file_path) as file:
        file_content = file.read()

    tree = ast.parse(file_content)

    class_file_dict = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_file_dict[node.name] = file_path

    return class_file_dict


def get_class_file_registry(folder_path, pattern_list):
    class_file_registry = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                if any(pattern in root for pattern in pattern_list):
                    class_file_dict = get_file_classes(
                        os.path.join(root, file)
                    )
                    class_file_registry.update(class_file_dict)
    return class_file_registry


def get_class_objects(file_path):
    class_objects = {}
    spec = importlib.util.spec_from_file_location("module.name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for class_name in dir(module):
        obj = getattr(module, class_name)
        if isinstance(obj, type):
            class_objects[class_name] = obj

    return class_objects


def unique_hash(n: int = 32) -> str:
    """unique random hash"""
    current_time = datetime.now().isoformat().encode("utf-8")
    random_bytes = os.urandom(42)
    return sha256(current_time + random_bytes).hexdigest()[:n]


def create_path(
    directory: Path | str,
    filename: str,
    extension: str = None,
    timestamp: bool = False,
    dir_exist_ok: bool = True,
    file_exist_ok: bool = False,
    time_prefix: bool = False,
    timestamp_format: str | None = None,
    random_hash_digits: int = 0,
) -> Path:
    if "/" in filename or "\\" in filename:
        raise ValueError("Filename cannot contain directory separators.")
    directory = Path(directory)

    name, ext = None, None
    if "." in filename:
        name, ext = filename.rsplit(".", 1)
    else:
        name = filename
        ext = extension.strip(".").strip() if extension else None

    if not ext:
        raise ValueError("No extension provided for filename.")

    ext = f".{ext}" if ext else ""

    if timestamp:
        timestamp_str = datetime.now().strftime(
            timestamp_format or "%Y%m%d%H%M%S"
        )
        name = (
            f"{timestamp_str}_{name}"
            if time_prefix
            else f"{name}_{timestamp_str}"
        )

    if random_hash_digits > 0:
        random_hash = "-" + unique_hash(random_hash_digits)
        name = f"{name}{random_hash}"

    full_filename = f"{name}{ext}"
    full_path = directory / full_filename

    if full_path.exists():
        if file_exist_ok:
            return full_path
        raise FileExistsError(
            f"File {full_path} already exists and file_exist_ok is False."
        )
    full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)
    return full_path


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
