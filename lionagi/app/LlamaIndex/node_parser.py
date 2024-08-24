from typing import Any

from lionagi.os.sys_util import SysUtil


def get_llamaindex_node_parser(node_parser: Any):

    NodeParser = SysUtil.check_import(
        package_name="llama_index",
        module_name="core.node_parser.interface",
        import_name="NodeParser",
        pip_name="llama-index",
    )

    if not isinstance(node_parser, str) and not issubclass(node_parser, NodeParser):
        raise TypeError("node_parser must be a string or NodeParser.")

    if isinstance(node_parser, str):
        if node_parser == "CodeSplitter":
            SysUtil.check_import("tree_sitter_languages")

        try:
            _parser = SysUtil.import_module(
                package_name="llama_index",
                module_name="core.node_parser",
            )
            return getattr(_parser, node_parser)
        except Exception as e:
            raise AttributeError(
                f"llama_index_core has no such attribute:" f" {node_parser}, Error: {e}"
            ) from e

    elif isinstance(node_parser, NodeParser):
        return node_parser


def llamaindex_parse_node(
    documents: list,
    node_parser: Any,
    *args,
    **kwargs,
):
    try:
        parser = get_llamaindex_node_parser(node_parser)
        try:
            parser = parser(*args, **kwargs)
        except Exception:
            parser = parser.from_defaults(*args, **kwargs)
        return parser.get_nodes_from_documents(documents)
    except Exception as e:
        raise ValueError(f"Failed to parse. Error: {e}") from e
