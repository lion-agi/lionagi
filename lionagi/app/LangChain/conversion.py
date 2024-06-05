from typing import Union, Callable, List, Dict, Any, TypeVar
from lionagi.os.libs.sys_util import check_import, change_dict_key

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

    check_import("langchain")
    from langchain.schema import Document as LangchainDocument

    dnode = datanode.to_dict()
    change_dict_key(dnode, old_key="content", new_key="page_content")
    change_dict_key(dnode, old_key="lc_id", new_key="id_")
    dnode = {**dnode, **kwargs}
    dnode = {k: v for k, v in dnode.items() if v is not None}
    if "page_content" not in dnode:
        dnode["page_content"] = ""

    return LangchainDocument(**dnode)
