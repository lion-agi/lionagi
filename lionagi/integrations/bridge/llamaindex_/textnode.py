from typing import Any, TypeVar
from lionagi.libs.sys_util import SysUtil


def to_llama_index_node(lion_node, node_type: Any = None,
                        **kwargs: Any) -> Any:

    SysUtil.check_import('llama_index', pip_name='llama-index')
    from llama_index.core.schema import BaseNode
    import llama_index.core.schema
    node_type = node_type or 'TextNode'

    _dict = lion_node.to_dict()
    SysUtil.change_dict_key(_dict, old_key='content', new_key='text')
    SysUtil.change_dict_key(_dict, old_key='node_id', new_key='id_')
    _dict['text'] = str(_dict['text'])
    _dict = {**_dict, **kwargs}

    if not isinstance(node_type, str) and not issubclass(node_type, BaseNode):
        raise TypeError(f'node_type must be a string or BaseNode')

    else:
        try:
            if isinstance(node_type, str) and hasattr(llama_index.core.schema, node_type):
                return getattr(llama_index.core.schema, node_type).from_dict(_dict)
            elif issubclass(node_type, BaseNode):
                return node_type.from_dict(_dict)
            else:
                raise AttributeError(f'Invalid llama-index node type: {node_type}')
        except Exception as e:
            raise AttributeError(f'Error: {e}')
