from typing import Any, Dict
from lionagi.os.lib.sys_util import change_dict_key, check_import
from .util import llama_meta_fields


def format_llama_index_meta(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the metadata of a llama index object to align with LionAGI schema.

    This function processes the input dictionary by renaming keys and
    extracting relevant fields to match the metadata schema requirements
    of LionAGI. It modifies the keys to adhere to the expected format and
    structures for LionAGI components.

    Args:
        data (Dict[str, Any]): The input dictionary containing llama index
                               metadata.

    Returns:
        Dict[str, Any]: The formatted dictionary with metadata aligned to
                        LionAGI schema.
    """
    change_dict_key(data, "text", "content")
    metadata = data.pop("metadata", {})

    for field in llama_meta_fields:
        metadata[field] = data.pop(field, None)

    change_dict_key(metadata, "class_name", "llama_index_class")
    change_dict_key(metadata, "id_", "llama_index_id")
    change_dict_key(metadata, "relationships", "llama_index_relationships")

    data["metadata"] = metadata
    return data


def format_lion_meta_to_llama_index(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the metadata of a LionAGI object to align with Llama Index schema.

    This function processes the input dictionary by renaming keys and
    extracting relevant fields to match the metadata schema requirements
    of Llama Index. It modifies the keys to adhere to the expected format
    and structures for Llama Index components.

    Args:
        data (Dict[str, Any]): The input dictionary containing LionAGI
                               metadata.

    Returns:
        Dict[str, Any]: The formatted dictionary with metadata aligned to
                        Llama Index schema.
    """
    change_dict_key(data, "content", "text")
    change_dict_key(data, "ln_id", "id_")

    if "metadata" in data:
        metadata = data["metadata"]
        change_dict_key(metadata, "llama_index_class", "class_name")
        change_dict_key(metadata, "llama_index_id", "id_")
        change_dict_key(metadata, "llama_index_relationships", "relationships")

        data["metadata"] = metadata

    return data


def to_llama_index_node(lion_node, node_type: Any = None, **kwargs: Any) -> Any:
    """
    Converts a Lion node to a Llama Index node of a specified type.

    This function takes a node from the Lion framework, converts it to a
    dictionary, modifies keys to match the expected Llama Index node schema,
    and then creates a Llama Index node object of the specified type.

    Args:
        lion_node: The Lion node to convert. Must have a `to_dict` method.
        node_type (Any, optional): The type of Llama Index node to create.
            Can be a string name of a node class within the Llama Index schema
            or a class that inherits from `BaseNode`. Defaults to 'TextNode'.
        **kwargs: Additional keyword arguments to be included in the Llama
                  Index node's initialization.

    Returns:
        Any: A new instance of the specified Llama Index node type populated
             with data from the Lion node.

    Raises:
        TypeError: If `node_type` is neither a string nor a subclass of
                   `BaseNode`.
        AttributeError: If an error occurs due to an invalid node type or
                        during the creation of the node object.
    """

    check_import("llama_index", pip_name="llama-index")
    from llama_index.core.schema import BaseNode, TextNode
    import llama_index.core.schema

    node_type = node_type or TextNode

    _dict = lion_node.to_dict()
    if _dict["content"] is None:
        _dict["content"] = ""
    formatted_meta = format_lion_meta_to_llama_index(_dict)
    _dict = {**formatted_meta, **kwargs}

    if not isinstance(node_type, str) and not issubclass(node_type, BaseNode):
        raise TypeError("node_type must be a string or BaseNode")

    try:
        if isinstance(node_type, str) and hasattr(llama_index.core.schema, node_type):
            return getattr(llama_index.core.schema, node_type).from_dict(_dict)

        elif issubclass(node_type, (BaseNode, TextNode)):
            return node_type.from_dict(_dict)

        else:
            raise AttributeError(f"Invalid llama-index node type: {node_type}")

    except Exception as e:
        raise AttributeError(f"Error: {e}")
