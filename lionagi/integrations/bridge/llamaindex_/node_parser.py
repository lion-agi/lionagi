from typing import Any

from lionfuncs import check_import, import_module

from lionagi.libs.sys_util import SysUtil


def get_llama_index_node_parser(node_parser: Any):
    """
    Retrieves a llama index node parser object based on the specified node parser name or class.

    This function checks if the specified node parser is a recognized type or name and returns the appropriate
    llama index node parser object. If a string is provided, it attempts to match it with known node parser names
    and import the corresponding node parser object dynamically. If a node parser class is provided, it validates
    that the class is a subclass of NodeParser.

    Args:
            node_parser (Any): The node parser identifier, which can be a node parser class, a string alias
                    for a node parser class, or None.

    Returns:
            Any: The llama index node parser object corresponding to the specified node parser.

    Raises:
            TypeError: If the node_parser is neither a string nor a subclass of NodeParser.
            AttributeError: If there is an issue importing the specified node parser due to it not being
            found within the llama_index.core.node_parser module.
    """

    NodeParser = check_import(
        "llama_index.core.node_parser.interface",
        import_name="NodeParser",
        pip_name="llama-index",
    )

    if not isinstance(node_parser, str) and not issubclass(
        node_parser, NodeParser
    ):
        raise TypeError("node_parser must be a string or NodeParser.")

    if isinstance(node_parser, str):
        if node_parser == "CodeSplitter":
            SysUtil.check_import("tree_sitter_languages")

        try:
            node_module = import_module(
                "llama_index.core", module_name="node_parser"
            )
            return getattr(node_module, node_parser)
        except Exception as e:
            raise AttributeError(
                f"llama_index_core has no such attribute:"
                f" {node_parser}, Error: {e}"
            ) from e

    elif isinstance(node_parser, NodeParser):
        return node_parser


def llama_index_parse_node(
    documents, node_parser: Any, parser_args=None, parser_kwargs=None
):
    """
    Parses documents using a specified llama index node parser and its arguments.

    This function initializes a llama index node parser with the given arguments and keyword arguments,
    then parses documents using the node parser's `get_nodes_from_documents` method.

    Args:
            documents (Any): The documents to be parsed by the node parser.
            node_parser (Any): The node parser to use. This can be a class, a string identifier, or None.
            parser_args (Optional[List[Any]], optional): Positional arguments to initialize the node parser.
            parser_kwargs (Optional[Dict[str, Any]], optional): Keyword arguments to initialize the node parser.

    Returns:
            Any: The nodes extracted from the documents by the node parser.

    Raises:
            ValueError: If there is an error initializing the node parser or parsing the documents.
    """

    try:
        parser_args = parser_args or []
        parser_kwargs = parser_kwargs or {}
        parser = get_llama_index_node_parser(node_parser)
        try:
            parser = parser(*parser_args, **parser_kwargs)
        except Exception:
            parser = parser.from_defaults(*parser_args, **parser_kwargs)
        return parser.get_nodes_from_documents(documents)
    except Exception as e:
        raise ValueError(f"Failed to parse. Error: {e}") from e
