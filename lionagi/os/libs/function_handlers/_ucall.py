"""
This module provides a unified call handler to execute functions asynchronously
with custom error handling.

The following functionalities are provided:
- ucall: Execute a function asynchronously with error handling.
"""

import asyncio
from typing import Any, Callable, Dict, Optional
from lionagi.os.libs.function_handlers._util import (
    is_coroutine_func,
    custom_error_handler,
    force_async,
)


async def ucall(
    func: Callable,
    *args: Any,
    error_map: Optional[Dict[type, Callable]] = None,
    **kwargs: Any,
) -> Any:
    """
    Execute a function asynchronously with error handling.

    This function checks if the given function is a coroutine. If not, it
    forces it to run asynchronously. It then executes the function, ensuring
    the proper handling of event loops. If an error occurs, it applies custom
    error handling based on the provided error map.

    Args:
        func (Callable): The function to be executed.
        *args (Any): Positional arguments to pass to the function.
        error_map (Optional[Dict[type, Callable]]): A dictionary mapping
            exception types to error handling functions. Defaults to None.
        **kwargs (Any): Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call.

    Raises:
        Exception: Propagates any exception raised during the function
            execution.
    """
    try:
        if not is_coroutine_func(func):
            func = force_async(func)

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
            custom_error_handler(e, error_map)
        raise e
