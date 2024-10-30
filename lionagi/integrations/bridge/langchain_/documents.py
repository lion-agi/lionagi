from collections.abc import Callable
from typing import Any, Dict, List, TypeVar, Union

from lionfuncs import check_import

from lionagi.libs.sys_util import SysUtil

T = TypeVar("T")


def to_langchain_document(datanode: T, **kwargs: Any) -> Any:
    """
    Converts a generic data node into a Langchain Document.

    This function transforms a node, typically from another data schema, into a Langchain Document format.
    It requires the source node to have a `to_dict` method to convert it into a dictionary, then it renames specific keys
    to match the Langchain Document schema before creating a Langchain Document object.

    Args:
            datanode (T): The data node to convert. Must have a `to_dict` method.
            **kwargs: Additional keyword arguments to be passed to the Langchain Document constructor.

    Returns:
            Any: An instance of `LangchainDocument` populated with data from the input node.
    """

    LangchainDocument = check_import(
        "langchain", module_name="schema", import_name="Document"
    )

    dnode = datanode.to_dict()
    SysUtil.change_dict_key(dnode, old_key="content", new_key="page_content")
    SysUtil.change_dict_key(dnode, old_key="lc_id", new_key="id_")
    dnode = {**dnode, **kwargs}
    dnode = {k: v for k, v in dnode.items() if v is not None}
    if "page_content" not in dnode:
        dnode["page_content"] = ""

    return LangchainDocument(**dnode)


def langchain_loader(
    loader: str | Callable,
    loader_args: list[Any] = [],
    loader_kwargs: dict[str, Any] = {},
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

    document_loaders = check_import(
        "langchain_community",
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
        loader_obj = loader(*loader_args, **loader_kwargs)
        data = loader_obj.load()
        return data
    except Exception as e:
        raise ValueError(f"Failed to load. Error: {e}")


def langchain_text_splitter(
    data: str | list,
    splitter: str | Callable,
    splitter_args: list[Any] = None,
    splitter_kwargs: dict[str, Any] = None,
) -> list[str]:
    """
    Splits text or a list of texts using a specified Langchain text splitter.

    This function allows for dynamic selection of a text splitter, either by name or as a function, to split text
    or documents into chunks. The splitter can be configured with additional arguments and keyword arguments.

    Args:
            data (Union[str, List]): The text or list of texts to be split.
            splitter (Union[str, Callable]): The name of the splitter function or the splitter function itself.
            splitter_args (List[Any], optional): Positional arguments to pass to the splitter function.
            splitter_kwargs (Dict[str, Any], optional): Keyword arguments to pass to the splitter function.

    Returns:
            List[str]: A list of text chunks produced by the text splitter.

    Raises:
            ValueError: If the splitter is invalid or fails during the split operation.
    """
    splitter_args = splitter_args or []
    splitter_kwargs = splitter_kwargs or {}

    SysUtil.check_import("langchain")
    import langchain_text_splitters as text_splitter

    try:
        if isinstance(splitter, str):
            splitter = getattr(text_splitter, splitter)
        else:
            splitter = splitter
    except Exception as e:
        raise ValueError(f"Invalid text splitter: {splitter}. Error: {e}")

    try:
        splitter_obj = splitter(*splitter_args, **splitter_kwargs)
        if isinstance(data, str):
            chunk = splitter_obj.split_text(data)
        else:
            chunk = splitter_obj.split_documents(data)
        return chunk
    except Exception as e:
        raise ValueError(f"Failed to split. Error: {e}")
