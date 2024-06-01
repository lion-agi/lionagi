from typing import Any, Callable
import asyncio
from ..data_handlers import to_list
from ._ucall import ucall


async def lcall(
    func: Callable,
    input_: list[Any],
    *,
    error_map: dict[type, Callable] = None,
    **kwargs,
):
    input_ = to_list(input_)
    tasks = [ucall(func, i, error_map=error_map, **kwargs) for i in input_]
    outs = await asyncio.gather(*tasks)
    return to_list(outs)
