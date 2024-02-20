from typing import Any, TypeVar
from llama_index.core.schema import TextNode
from lionagi.schema import DataNode

T = TypeVar('T', bound='DataNode')


def from_llama_index_node(llama_node: Any, **kwargs: Any) -> T:
    _dict = llama_node.to_dict(**kwargs)
    return DataNode.from_dict(_dict)


def to_llama_index_node(lion_node: T, node_type: str | TextNode = None,
                        **kwargs: Any) -> TextNode | None:

    node_type = node_type or TextNode

    _dict = lion_node.to_dict()
    change_dict_key(_dict, old_key='content', new_key='text')
    change_dict_key(_dict, old_key='node_id', new_key='id_')
    _dict['text'] = str(_dict['text'])
    _dict = {**_dict, **kwargs}

    if not isinstance(node_type, (str, TextNode)):
        raise TypeError(f'node_type must be a string or TextNode, not {type(node_type)}')

    elif isinstance(node_type, TextNode):
        return TextNode.from_dict(_dict)

    elif isinstance(node_type, str):
        try:
            if hasattr(llama_index.core.schema, node_type):
                return getattr(llama_index.core.schema, node_type).from_dict(_dict)
            else:
                raise AttributeError(f'No such attribute: {node_type}')
        except Exception as e:
            raise AttributeError(f'Error: {e}')
