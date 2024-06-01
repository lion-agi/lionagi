import asyncio
from typing import Any, Callable
from ..sys_util import get_now
from ._tcall import tcall


async def rcall(
    func: Callable,
    *args,
    retries: int = 0,
    delay: float = 0.1,
    backoff_factor: float = 2,
    default: Any = None,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    **kwargs,
) -> Any:
    last_exception = None
    result = None

    start = get_now(datetime_=False)
    for attempt in range(retries + 1) if retries == 0 else range(retries):
        try:
            err_msg = f"Attempt {attempt + 1}/{retries}: " if retries > 0 else None
            if timing:
                return (
                    await tcall(
                        func, *args, err_msg=err_msg, timeout=timeout, **kwargs
                    ),
                    get_now(datetime_=False) - start,
                )

            return await tcall(func, *args, timeout=timeout, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < retries:
                if verbose:
                    print(f"Attempt {attempt + 1}/{retries} failed: {e}, retrying...")
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                break
    if result is None and default is not None:
        return default
    elif last_exception is not None:
        raise RuntimeError(
            f"Operation failed after {retries+1} attempts: {last_exception}"
        ) from last_exception
    else:
        raise RuntimeError("rcall failed without catching an exception")
