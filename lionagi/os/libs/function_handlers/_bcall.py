from typing import Any, Callable
from ..data_handlers import to_list
from ._lcall import lcall


async def bcall(input_: Any, func: Callable, batch_size: int, *args, **kwargs):
    results = []
    input_ = to_list(input_)
    for i in range(0, len(input_), batch_size):
        batch = input_[i : i + batch_size]
        batch_results = await lcall(func, batch, *args, **kwargs)
        yield batch_results

        results.extend(batch_results)
    return results
