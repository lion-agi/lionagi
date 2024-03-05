from typing import Any
from lionagi.libs.sys_util import SysUtil


def get_llama_index_node_parser(node_parser: Any):

    SysUtil.check_import('llama_index', pip_name='llama-index')
    from llama_index.core.node_parser.interface import NodeParser
    import llama_index.core.node_parser

    if not isinstance(node_parser, str) and not issubclass(node_parser, NodeParser):
        raise TypeError(
            f'node_parser must be a string or NodeParser.')

    if isinstance(node_parser, str):
        if node_parser == 'CodeSplitter':
            SysUtil.check_import('tree_sitter_languages')

        try:
            parser = getattr(llama_index.core.node_parser, node_parser)
            return parser
        except Exception as e:
            raise AttributeError(f"llama_index_core has no such attribute:"
                                 f" {node_parser}, Error: {e}")

    elif isinstance(node_parser, NodeParser):
        return node_parser


def llama_index_parse_node(documents, node_parser: Any,
                           parser_args=None, parser_kwargs=None):
    try:
        parser_args = parser_args or []
        parser_kwargs = parser_kwargs or {}
        parser = get_llama_index_node_parser(node_parser)
        try:
            parser = parser(*parser_args, **parser_kwargs)
        except:
            parser = parser.from_defaults(*parser_args, **parser_kwargs)
        nodes = parser.get_nodes_from_documents(documents)
        return nodes

    except Exception as e:
        raise ValueError(f'Failed to parse. Error: {e}')
