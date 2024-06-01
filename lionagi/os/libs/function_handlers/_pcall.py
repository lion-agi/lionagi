from asyncio import gather
from typing import Callable, Any, List
from ._ucall import ucall


async def pcall(funcs: List[Callable[..., Any]]) -> List[Any]:
    """
    Concurrently call multiple asynchronous functions.

    This function accepts a list of asynchronous functions, calls them concurrently
    using asyncio, and returns their results.

    Args:
        funcs (List[Callable[..., Any]]): A list of asynchronous functions to be
            called.

    Returns:
        List[Any]: A list of results from the called functions.

    Examples:
        >>> async def foo():
        >>>     await asyncio.sleep(1)
        >>>     return "foo"
        >>>
        >>> async def bar():
        >>>     await asyncio.sleep(2)
        >>>     return "bar"
        >>>
        >>> async def main():
        >>>     results = await pcall([foo, bar])
        >>>     print(results)
        >>>
        >>> asyncio.run(main())
    """
    tasks = [ucall(func) for func in funcs]
    return await gather(*tasks)
