from typing import Any, Callable
import asyncio
from ..sys_util import get_now
from ._ucall import ucall


async def tcall(
    func: Callable,
    *args,
    initial_delay: float = 0,
    err_msg: str | None = None,
    surpress_err: bool = False,
    timing: bool = False,
    timeout: float | None = None,
    default: Any = None,
    **kwargs,
) -> Any:

    start = get_now(datetime_=False)

    try:
        await asyncio.sleep(initial_delay)
        result = None

        if timeout is None:
            result = await ucall(func, *args, **kwargs)

        else:
            try:
                result = await asyncio.wait_for(
                    ucall(func, *args, **kwargs), timeout=timeout
                )

            except asyncio.TimeoutError as e:
                err_msg = f"{err_msg or ''}Timeout {timeout} seconds exceeded"
                if surpress_err:
                    duration = get_now(datetime_=False) - start
                    return default, duration if timing else default

                else:
                    raise asyncio.TimeoutError(err_msg)

        duration = get_now(datetime_=False) - start
        return result, duration if timing else result

    except Exception as e:
        err_msg = (
            f"{err_msg} Error: {e}"
            if err_msg
            else f"An error occurred in async execution: {e}"
        )
        if surpress_err:
            duration = get_now(datetime_=False) - start
            return default, duration if timing else default
        else:
            raise RuntimeError(err_msg)
