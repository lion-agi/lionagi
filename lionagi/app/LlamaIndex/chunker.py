def _llama_index_chunker(
    documents,
    documents_convert_func,
    chunker,
    chunker_args,
    chunker_kwargs,
    to_lion: bool | Callable,
):
    """
    Chunks documents using a LlamaIndex chunker.

    Args:
        documents (list): List of documents to be chunked.
        documents_convert_func (Callable): Function to convert documents.
        chunker (str | Callable): The chunker function or its name.
        chunker_args (list): Positional arguments for the chunker function.
        chunker_kwargs (dict): Keyword arguments for the chunker function.
        to_lion (bool | Callable): Whether to convert the data to Node instances or a custom parser.

    Returns:
        pile: A pile of chunked Node instances or custom parsed nodes.

    Example usage:
        >>> chunked_docs = _llama_index_chunker(docs, convert_func, llama_chunker, ['arg1'], {'key': 'value'}, True)
    """
    if documents_convert_func:
        documents = documents_convert_func(documents, "llama_index")
    nodes = LlamaIndexBridge.llama_index_parse_node(
        documents, chunker, chunker_args, chunker_kwargs
    )

    if isinstance(to_lion, bool) and to_lion is True:
        nodes = [Node.from_llama_index(i) for i in nodes]
    elif isinstance(to_lion, Callable):
        nodes = _datanode_parser(nodes, to_lion)
    return nodes
