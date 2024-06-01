from typing import Any
from asyncio import gather
from ..data_handlers import to_list
from ._ucall import ucall
from ._lcall import lcall


async def mcall(input_, /, func: Any, *, explode: bool = False, **kwargs):
    input_ = to_list(input_)
    func = to_list(func)

    if explode:
        tasks = [lcall(input_, f, flatten=True, **kwargs) for f in func]
        return await gather(*tasks)

    elif len(input_) == len(func):
        tasks = [ucall(func, inp, **kwargs) for inp, func in zip(input_, func)]
        return await gather(*tasks)

    else:
        raise ValueError(
            "Inputs and functions must be the same length for map calling."
        )
