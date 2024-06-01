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
) -> list[Any]:
    """
    Apply a function concurrently to each element of a list using asyncio.

    This function converts the input to a list, creates an asyncio task for
    each element by applying the provided function, and gathers the results
    concurrently. It handles any errors using an optional error mapping.

    Args:
        func (Callable): The function to apply to each element of the input
            list.
        input_ (list[Any]): The input list of elements to process.
        error_map (dict[type, Callable], optional): A dictionary mapping
            exception types to error handling functions. Defaults to None.
        **kwargs: Additional keyword arguments to pass to `ucall`.

    Returns:
        list[Any]: The list of results after processing all elements
            concurrently.

    Examples:
        >>> async def process_item(item):
        >>>     if item == 2:
        >>>         raise ValueError("Test error")
        >>>     return item * 2
        >>>
        >>> async def handle_value_error(e):
        >>>     return f"Handled {e}"
        >>>
        >>> async def main():
        >>>     data = [1, 2, 3]
        >>>     error_map = {ValueError: handle_value_error}
        >>>     results = await lcall(process_item, data, error_map=error_map)
        >>>     print(results)
        >>>
        >>> asyncio.run(main())
    """
    input_ = to_list(input_)
    tasks = [ucall(func, i, error_map=error_map, **kwargs) for i in input_]
    outs = await asyncio.gather(*tasks)
    return to_list(outs)
