from typing import Any, Callable
from lionagi.os.primitives import Node, Pile, pile


def langchain_loader(loader: str | Callable, /, *args, **kwargs) -> list[Any]:

    from lionagi.os.sys_utils import SysUtil

    document_loaders = SysUtil.check_import(
        package_name="langchain_community",
        module_name="document_loaders",
        pip_name="langchain",
    )

    try:
        if isinstance(loader, str):
            loader = getattr(document_loaders, loader)
        else:
            loader = loader
    except Exception as e:
        raise ValueError(f"Invalid loader: {loader}. Error: {e}")

    try:
        loader_obj = loader(*args, **kwargs)
        data = loader_obj.load()
        return data
    except Exception as e:
        raise ValueError(f"Failed to load. Error: {e}")


def langchain_reader(reader, /, *args, **kwargs) -> Pile:
    nodes = langchain_loader(loader=reader, *args, **kwargs)
    return pile(items=[Node.from_obj(i) for i in nodes])
