from typing import Any, Callable, Dict, List, Union
from lionagi.os.libs.sys_util import check_import


def langchain_loader(
    loader: Union[str, Callable],
    loader_args: List[Any] = [],
    loader_kwargs: Dict[str, Any] = {},
) -> Any:
    """
    Initializes and uses a specified loader to load data within the Langchain ecosystem.

    This function supports dynamically selecting a loader by name or directly using a loader function.
    It passes specified arguments and keyword arguments to the loader for data retrieval or processing.

    Args:
            loader (Union[str, Callable]): A string representing the loader's name or a callable loader function.
            loader_args (List[Any], optional): A list of positional arguments for the loader.
            loader_kwargs (Dict[str, Any], optional): A dictionary of keyword arguments for the loader.

    Returns:
            Any: The result returned by the loader function, typically data loaded into a specified format.

    Raises:
            ValueError: If the loader cannot be initialized or fails to load data.

    Examples:
            >>> data = langchain_loader("json_loader", loader_args=["data.json"])
            >>> isinstance(data, dict)
            True
    """

    check_import("langchain")
    import langchain_community.document_loaders as document_loaders

    try:
        if isinstance(loader, str):
            loader = getattr(document_loaders, loader)
        else:
            loader = loader
    except Exception as e:
        raise ValueError(f"Invalid loader: {loader}. Error: {e}")

    try:
        loader_obj = loader(*loader_args, **loader_kwargs)
        data = loader_obj.load()
        return data
    except Exception as e:
        raise ValueError(f"Failed to load. Error: {e}")
