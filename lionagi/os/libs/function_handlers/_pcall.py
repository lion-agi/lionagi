from asyncio import gather
from ._ucall import ucall


async def pcall(funcs):
    task = [ucall(func) for func in funcs]
    return await gather(*task)
