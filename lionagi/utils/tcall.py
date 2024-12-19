import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

from ._utils import is_coro_func
from .undefined import Undefined

T = TypeVar("T")


async def tcall(
    func: Callable[..., T],
    /,
    *args: Any,
    initial_delay: float = 0,
    timing: bool = False,
    timeout: float | None = None,
    default: Any = Undefined,
    error_msg: str | None = None,
    error_map: dict[type, Callable[[Exception], None]] | None = None,
    **kwargs: Any,
) -> T | tuple[T, float]:
    """Execute a function asynchronously with timing and error handling.

    Executes a synchronous or asynchronous function with optional timing,
    timeout, and error handling capabilities. Can delay execution and provide
    detailed error feedback.

    Args:
        func: Function or coroutine to execute.
        *args: Positional arguments passed to func.
        initial_delay: Seconds to wait before execution. Defaults to 0.
        timing: If True, returns tuple of (result, duration). Defaults to False.
        timeout: Maximum seconds to wait for completion. None for no timeout.
        default: Value returned on error if provided, otherwise error is raised.
        error_msg: Optional prefix for error messages.
        error_map: Dict mapping exception types to handler functions.
        **kwargs: Keyword arguments passed to func.

    Returns:
        If timing=False:
            Result of func execution or default value on error
        If timing=True:
            Tuple of (result, duration_in_seconds)

    Raises:
        asyncio.TimeoutError: If execution exceeds timeout and no default set.
        RuntimeError: If execution fails and no default or handler exists.

    Examples:
        >>> async def example():
        ...     result = await tcall(
        ...         slow_function,
        ...         timeout=5,
        ...         default="timeout",
        ...         timing=True
        ...     )
        ...     print(result)  # ("result", 1.234) or ("timeout", 5.0)
    """
    loop = asyncio.get_running_loop()
    start = loop.time()

    def finalize(result: Any) -> Any:
        """Wrap result with timing information if requested."""
        if timing:
            duration = loop.time() - start
            return (result, duration)
        return result

    try:
        if initial_delay > 0:
            await asyncio.sleep(initial_delay)

        if is_coro_func(func):
            # Handle coroutine function
            if timeout is not None:
                result = await asyncio.wait_for(
                    func(*args, **kwargs), timeout=timeout
                )
            else:
                result = await func(*args, **kwargs)
        else:
            # Handle synchronous function
            if timeout is not None:
                coro = asyncio.to_thread(func, *args, **kwargs)
                result = await asyncio.wait_for(coro, timeout=timeout)
            else:
                result = func(*args, **kwargs)

        return finalize(result)

    except TimeoutError as e:
        if default is not Undefined:
            return finalize(default)
        msg = f"{error_msg or ''} Timeout {timeout} seconds exceeded".strip()
        raise TimeoutError(msg) from e

    except Exception as e:
        if error_map is not None:
            handler = error_map.get(type(e))
            if handler:
                handler(e)
                return finalize(None)

        if default is not Undefined:
            return finalize(default)

        msg = (
            f"{error_msg} Error: {e}"
            if error_msg
            else f"An error occurred in async execution: {e}"
        )
        raise RuntimeError(msg) from e
