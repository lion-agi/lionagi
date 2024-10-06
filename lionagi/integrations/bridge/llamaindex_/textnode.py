from typing import Any, TypeVar

from lionagi.libs.sys_util import SysUtil


def to_llama_index_node(
    lion_node, node_type: Any = None, **kwargs: Any
) -> Any:
    """
    Converts a Lion node to a Llama Index node of a specified type.

    This function takes a node from the Lion framework, converts it to a dictionary, modifies keys to match
    the expected Llama Index node schema, and then creates a Llama Index node object of the specified type.

    Args:
            lion_node: The Lion node to convert. Must have a `to_dict` method.
            node_type (Any, optional): The type of Llama Index node to create. Can be a string name of a node class
                    within the Llama Index schema or a class that inherits from `BaseNode`. Defaults to 'TextNode'.
            **kwargs: Additional keyword arguments to be included in the Llama Index node's initialization.

    Returns:
            Any: A new instance of the specified Llama Index node type populated with data from the Lion node.

    Raises:
            TypeError: If `node_type` is neither a string nor a subclass of `BaseNode`.
            AttributeError: If an error occurs due to an invalid node type or during the creation of the node object.
    """

    SysUtil.check_import("llama_index", pip_name="llama-index")
    import llama_index.core.schema
    from llama_index.core.schema import BaseNode

    node_type = node_type or "TextNode"

    _dict = lion_node.to_dict()
    SysUtil.change_dict_key(_dict, old_key="content", new_key="text")
    SysUtil.change_dict_key(_dict, old_key="node_id", new_key="id_")
    _dict["text"] = str(_dict["text"])
    _dict = {**_dict, **kwargs}

    if not isinstance(node_type, str) and not issubclass(node_type, BaseNode):
        raise TypeError(f"node_type must be a string or BaseNode")

    else:
        try:
            if isinstance(node_type, str) and hasattr(
                llama_index.core.schema, node_type
            ):
                return getattr(llama_index.core.schema, node_type).from_dict(
                    _dict
                )
            elif issubclass(node_type, BaseNode):
                return node_type.from_dict(_dict)
            else:
                raise AttributeError(
                    f"Invalid llama-index node type: {node_type}"
                )
        except Exception as e:
            raise AttributeError(f"Error: {e}")
