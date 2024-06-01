import asyncio
from typing import Any, Callable
from ._util import is_coroutine_func, custom_error_handler, force_async


# unified call handler
async def ucall(
    func: Callable, *args, error_map: dict[type, Callable] = None, **kwargs
) -> Any:
    try:
        if not is_coroutine_func(func):
            func = force_async(func)

        # Checking for a running event loop
        try:
            loop = asyncio.get_running_loop()
            return (
                await func(*args, **kwargs)
                if loop.is_running()
                else await asyncio.run(func(*args, **kwargs))
            )

        except RuntimeError:  # No running event loop
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(func(*args, **kwargs))

            loop.close()
            return result

    except Exception as e:
        if error_map:
            custom_error_handler(e, error_map)
        raise
