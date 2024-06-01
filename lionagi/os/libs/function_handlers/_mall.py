from typing import Any
from asyncio import gather
from ..data_handlers import to_list
from ._ucall import ucall
from ._lcall import lcall


async def mcall(
    input_: Any,
    /,
    func: Any,
    *,
    explode: bool = False,
    **kwargs,
) -> list[Any]:
    """
    Concurrently apply multiple functions to multiple inputs with optional
    explosion.

    This function applies a list of functions to a list of inputs concurrently
    using asyncio. It supports two modes: explode mode, where each function is
    applied to the entire list of inputs, and map mode, where each function is
    applied to the corresponding input.

    Args:
        input_ (Any): The input data to be processed, which will be converted
            to a 1-dimensional list.
        func (Any): The function or list of functions to be applied.
        explode (bool, optional): If True, each function is applied to the
            entire list of inputs. If False, each function is applied to the
            corresponding input. Defaults to False.
        **kwargs: Additional keyword arguments to pass to `ucall` or `lcall`.

    Returns:
        list[Any]: The list of results after processing all functions
            concurrently.

    Raises:
        ValueError: If the lengths of `input_` and `func` do not match when
            `explode` is False.

    Examples:
        >>> async def process_item(item):
        >>>     return item * 2
        >>>
        >>> async def main():
        >>>     data = [1, 2, 3]
        >>>     funcs = [process_item, process_item, process_item]
        >>>     results = await mcall(data, funcs, explode=True)
        >>>     print(results)
        >>>
        >>> asyncio.run(main())
    """
    input_ = to_list(input_)
    func = to_list(func)

    if explode:
        tasks = [lcall(input_, f, flatten=True, **kwargs) for f in func]
        return await gather(*tasks)
    elif len(input_) == len(func):
        tasks = [ucall(f, inp, **kwargs) for inp, f in zip(input_, func)]
        return await gather(*tasks)
    else:
        raise ValueError(
            "Inputs and functions must be the same length for map calling."
        )
