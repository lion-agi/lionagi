# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

from ._utils import is_coro_func
from .to_list import to_list
from .undefined import Undefined

T = TypeVar("T")


async def alcall(
    input_: list[Any],
    func: Callable[..., T],
    /,
    *,
    sanitize_input: bool = False,
    unique_input: bool = False,
    num_retries: int = 0,
    initial_delay: float = 0,
    retry_delay: float = 0,
    backoff_factor: float = 1,
    retry_default: Any = Undefined,
    retry_timeout: float | None = None,
    retry_timing: bool = False,
    max_concurrent: int | None = None,
    throttle_period: float | None = None,
    flatten: bool = False,
    dropna: bool = False,
    unique_output: bool = False,
    flatten_tuple_set: bool = False,
    **kwargs: Any,
) -> list[T] | list[tuple[T, float]]:
    """
    Asynchronously apply a function to each element of a list, with optional input sanitization,
    retries, timeout, and output processing.

    Args:
        input_ (list[Any]): The list of inputs to process.
        func (Callable[..., T]): The function to apply (async or sync).
        sanitize_input (bool): If True, input is flattened, dropna applied, and made unique if unique_input.
        unique_input (bool): If True and sanitize_input is True, input is made unique.
        num_retries (int): Number of retry attempts on exception.
        initial_delay (float): Initial delay before starting executions.
        retry_delay (float): Delay between retries.
        backoff_factor (float): Multiplier for delay after each retry.
        retry_default (Any): Default value if all retries fail.
        retry_timeout (float | None): Timeout for each function call.
        retry_timing (bool): If True, return (result, duration) tuples.
        max_concurrent (int | None): Maximum number of concurrent operations.
        throttle_period (float | None): Delay after each completed operation.
        flatten (bool): Flatten the final result if True.
        dropna (bool): Remove None values from the final result if True.
        unique_output (bool): Deduplicate the output if True.
        **kwargs: Additional arguments passed to func.

    Returns:
        list[T] or list[tuple[T, float]]: The processed results, or results with timing if retry_timing is True.

    Raises:
        asyncio.TimeoutError: If a call times out and no default is provided.
        Exception: If retries are exhausted and no default is provided.
    """

    # Validate func is a single callable
    if not callable(func):
        # If func is not callable, maybe it's an iterable. Extract one callable if possible.
        try:
            func_list = list(func)  # Convert iterable to list
        except TypeError:
            raise ValueError(
                "func must be callable or an iterable containing one callable."
            )

        # Ensure exactly one callable is present
        if len(func_list) != 1 or not callable(func_list[0]):
            raise ValueError("Only one callable function is allowed.")

        func = func_list[0]

    # Process input if requested
    if sanitize_input:
        input_ = to_list(
            input_,
            flatten=True,
            dropna=True,
            unique=unique_input,
            flatten_tuple_set=flatten_tuple_set,
        )
    else:
        if not isinstance(input_, list):
            # Attempt to iterate
            try:
                iter(input_)
                # It's iterable (tuple), convert to list of its contents
                input_ = list(input_)
            except TypeError:
                # Not iterable, just wrap in a list
                input_ = [input_]

    # Optional initial delay before processing
    if initial_delay:
        await asyncio.sleep(initial_delay)

    semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
    throttle_delay = throttle_period or 0
    coro_func = is_coro_func(func)

    async def call_func(item: Any) -> T:
        if coro_func:
            # Async function
            if retry_timeout is not None:
                return await asyncio.wait_for(
                    func(item, **kwargs), timeout=retry_timeout
                )
            else:
                return await func(item, **kwargs)
        else:
            # Sync function
            if retry_timeout is not None:
                return await asyncio.wait_for(
                    asyncio.to_thread(func, item, **kwargs),
                    timeout=retry_timeout,
                )
            else:
                return func(item, **kwargs)

    async def execute_task(i: Any, index: int) -> Any:
        start_time = asyncio.get_running_loop().time()
        attempts = 0
        current_delay = retry_delay
        while True:
            try:
                result = await call_func(i)
                if retry_timing:
                    end_time = asyncio.get_running_loop().time()
                    return index, result, end_time - start_time
                else:
                    return index, result
            except Exception:
                attempts += 1
                if attempts <= num_retries:
                    if current_delay:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    # Retry loop continues
                else:
                    # Exhausted retries
                    if retry_default is not Undefined:
                        # Return default if provided
                        if retry_timing:
                            end_time = asyncio.get_running_loop().time()
                            duration = end_time - (start_time or end_time)
                            return index, retry_default, duration
                        else:
                            return index, retry_default
                    # No default, re-raise
                    raise

    async def task_wrapper(item: Any, idx: int) -> Any:
        if semaphore:
            async with semaphore:
                return await execute_task(item, idx)
        else:
            return await execute_task(item, idx)

    # Create tasks
    tasks = [task_wrapper(item, idx) for idx, item in enumerate(input_)]

    # Collect results as they complete
    results = []
    for coro in asyncio.as_completed(tasks):
        res = await coro
        results.append(res)
        if throttle_delay:
            await asyncio.sleep(throttle_delay)

    # Sort by original index
    results.sort(key=lambda x: x[0])

    if retry_timing:
        # (index, result, duration)
        filtered = [
            (r[1], r[2]) for r in results if not dropna or r[1] is not None
        ]
        return filtered
    else:
        # (index, result)
        output_list = [r[1] for r in results]
        return to_list(
            output_list,
            flatten=flatten,
            dropna=dropna,
            unique=unique_output,
            flatten_tuple_set=flatten_tuple_set,
        )
