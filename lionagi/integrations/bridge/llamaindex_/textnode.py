# from typing import Any, TypeVar
# from lionagi.util import SysUtil
# from lionagi.util.import_util import ImportUtil


# def to_llama_index_node(lion_node, node_type: Any = None,
#                         **kwargs: Any) -> Any:

#     ImportUtil.check_import('llama-index')
#     import llama_index
#     from llama_index.core.schema import TextNode
#     node_type = node_type or TextNode

#     _dict = lion_node.to_dict()
#     SysUtil.change_dict_key(_dict, old_key='content', new_key='text')
#     SysUtil.change_dict_key(_dict, old_key='node_id', new_key='id_')
#     _dict['text'] = str(_dict['text'])
#     _dict = {**_dict, **kwargs}

#     if not isinstance(node_type, (str, TextNode)):
#         raise TypeError(f'node_type must be a string or TextNode, not {type(node_type)}')

#     elif isinstance(node_type, TextNode):
#         return TextNode.from_dict(_dict)

#     elif isinstance(node_type, str):
#         try:
#             if hasattr(llama_index.core.schema, node_type):
#                 return getattr(llama_index.core.schema, node_type).from_dict(_dict)
#             else:
#                 raise AttributeError(f'No such attribute: {node_type}')
#         except Exception as e:
#             raise AttributeError(f'Error: {e}')
