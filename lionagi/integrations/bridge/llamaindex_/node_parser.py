# from typing import Any
# from lionagi.util import SysUtil, to_list
# from lionagi.util.import_util import ImportUtil

# def get_llama_index_node_parser(node_parser: Any ):

#     ImportUtil.check_import('llama-index')
#     import llama_index
#     from llama_index.core.node_parser.interface import NodeParser

#     if not isinstance(node_parser, [str]):
#         raise TypeError(
#             f'node_parser must be a string or NodeParser, not {type(node_parser)}')

#     if isinstance(node_parser, str):
#         if node_parser == 'CodeSplitter':
#             SysUtil.check_import('tree_sitter_languages')

#         try:
#             parser = getattr(llama_index.core.node_parser, node_parser)
#             return parser
#         except Exception as e:
#             raise AttributeError(f"llama_index_core has no such attribute:"
#                                  f" {node_parser}, Error: {e}")

#     elif isinstance(node_parser, NodeParser):
#         return node_parser


# def llama_index_parse_node(documents, node_parser: Any,
#                            parser_args=None, parser_kwargs=None):
#     parser_args = parser_args or []
#     parser_kwargs = parser_kwargs or {}
#     parser = get_llama_index_node_parser(node_parser)

#     ImportUtil.check_import('llama-index')
#     import llama_index
#     from llama_index.core.schema import Document as LlamaDocument

#     if isinstance(to_list(documents)[0], LlamaDocument):
#         nodes = parser.get_nodes_from_documents(documents, *parser_args, **parser_kwargs)
#     else:
#         try:
#             dict_ = [LlamaDocument.from_dict(doc.to_dict()) for doc in
#                      to_list(documents, dropna=True)]
#             nodes = parser.get_nodes_from_documents(dict_, *parser_args, **parser_kwargs)
#         except Exception as e:
#             raise ValueError(f'Failed to parse. Error: {e}')
