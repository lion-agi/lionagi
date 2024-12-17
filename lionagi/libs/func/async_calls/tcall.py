import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, Field

from ...constants import UNDEFINED
from ..utils import is_coroutine_func

T = TypeVar("T")

__all__ = (
    "TCallParams",
    "tcall",
)


class TCallParams(BaseModel):
    """Configuration parameters for timed function calls with error handling.

    Attributes:
        kwargs: Additional keyword arguments for the function call
        delay: Pre-execution delay in seconds
        error_msg: Custom error message prefix
        timing: Return execution duration if True
        timeout: Maximum execution time in seconds
        default: Fallback value on error/timeout
        error_map: Custom exception handlers {ExceptionType: handler_func}
    """

    kwargs: dict = Field(default_factory=dict)
    delay: float = 0
    error_msg: str | None = None
    timing: bool = False
    timeout: float | None = None
    default: Any = UNDEFINED
    error_map: dict[type, Callable[[Exception], None]] | None = None

    async def __call__(self, func=None, *args, **kwargs) -> T:
        """Execute function with configured parameters."""
        return await tcall(
            func,
            args=args,
            kwargs={**kwargs, **self.kwargs},
            delay=self.delay,
            error_msg=self.error_msg,
            timing=self.timing,
            timeout=self.timeout,
            default=self.default,
            error_map=self.error_map,
        )

    def __str__(self) -> str:
        return f"TCallParams({', '.join(f'{k}={v}' for k,v in self.__dict__.items())})"

    __repr__ = __str__


async def tcall(
    func: Callable[..., T],
    /,
    args: Any = [],
    kwargs: dict = {},
    delay: float = 0,
    error_msg: str | None = None,
    timing: bool = False,
    timeout: float | None = None,
    default: Any = UNDEFINED,
    error_map: dict[type, Callable[[Exception], None]] | None = None,
) -> T | tuple[T, float]:
    """Execute function with timing, error handling, and timeout control.

    Args:
        func: Target function to execute
        args: Positional arguments
        kwargs: Keyword arguments
        delay: Pre-execution delay (seconds)
        error_msg: Custom error message prefix
        timing: Return execution duration if True
        timeout: Maximum execution time (seconds)
        default: Fallback value on error/timeout
        error_map: Custom exception handlers

    Returns:
        Function result or (result, duration) if timing=True

    Raises:
        TimeoutError: On execution timeout if no default provided
        RuntimeError: On execution error if no default/handler provided
    """
    start = asyncio.get_event_loop().time()

    try:
        await asyncio.sleep(delay)
        result = None

        if is_coroutine_func(func):
            # Asynchronous function
            if timeout is None:
                result = await func(*args, **kwargs)
            else:
                result = await asyncio.wait_for(
                    func(*args, **kwargs), timeout=timeout
                )
        else:
            # Synchronous function
            if timeout is None:
                result = func(*args, **kwargs)
            else:
                result = await asyncio.wait_for(
                    asyncio.shield(asyncio.to_thread(func, *args, **kwargs)),
                    timeout=timeout,
                )

        duration = asyncio.get_event_loop().time() - start
        return (result, duration) if timing else result

    except TimeoutError as e:
        error_msg = f"{error_msg or ''} Timeout {timeout} seconds exceeded"
        if default is not UNDEFINED:
            duration = asyncio.get_event_loop().time() - start
            return (default, duration) if timing else default
        else:
            raise TimeoutError(error_msg) from e

    except Exception as e:
        if error_map and type(e) in error_map:
            error_map[type(e)](e)
            duration = asyncio.get_event_loop().time() - start
            return (None, duration) if timing else None
        error_msg = (
            f"{error_msg} Error: {e}"
            if error_msg
            else f"An error occurred in async execution: {e}"
        )
        if default is not UNDEFINED:
            duration = asyncio.get_event_loop().time() - start
            return (default, duration) if timing else default
        else:
            raise RuntimeError(error_msg) from e
