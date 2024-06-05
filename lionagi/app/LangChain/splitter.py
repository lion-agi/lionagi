def langchain_text_splitter(
    data: Union[str, List],
    splitter: Union[str, Callable],
    splitter_args: List[Any] = None,
    splitter_kwargs: Dict[str, Any] = None,
) -> List[str]:
    """
    Splits text or a list of texts using a specified Langchain text splitter.

    This function allows for dynamic selection of a text splitter, either by name or as a function, to split text
    or documents into chunks. The splitter can be configured with additional arguments and keyword arguments.

    Args:
            data (Union[str, List]): The text or list of texts to be split.
            splitter (Union[str, Callable]): The name of the splitter function or the splitter function itself.
            splitter_args (List[Any], optional): Positional arguments to pass to the splitter function.
            splitter_kwargs (Dict[str, Any], optional): Keyword arguments to pass to the splitter function.

    Returns:
            List[str]: A list of text chunks produced by the text splitter.

    Raises:
            ValueError: If the splitter is invalid or fails during the split operation.
    """
    splitter_args = splitter_args or []
    splitter_kwargs = splitter_kwargs or {}

    check_import("langchain")
    import langchain_text_splitters as text_splitter

    try:
        if isinstance(splitter, str):
            splitter = getattr(text_splitter, splitter)
        else:
            splitter = splitter
    except Exception as e:
        raise ValueError(f"Invalid text splitter: {splitter}. Error: {e}")

    try:
        splitter_obj = splitter(*splitter_args, **splitter_kwargs)
        if isinstance(data, str):
            chunk = splitter_obj.split_text(data)
        else:
            chunk = splitter_obj.split_documents(data)
        return chunk
    except Exception as e:
        raise ValueError(f"Failed to split. Error: {e}")


def _langchain_chunker(
    documents,
    documents_convert_func,
    chunker,
    chunker_args,
    chunker_kwargs,
    to_lion: bool | Callable,
):
    """
    Chunks documents using a Langchain chunker.

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
        >>> chunked_docs = _langchain_chunker(docs, convert_func, langchain_chunker, ['arg1'], {'key': 'value'}, True)
    """
    if documents_convert_func:
        documents = documents_convert_func(documents, "langchain")
    nodes = LangchainBridge.langchain_text_splitter(
        documents, chunker, chunker_args, chunker_kwargs
    )
    if isinstance(to_lion, bool) and to_lion is True:
        if isinstance(documents, str):
            nodes = [Node(content=i) for i in nodes]
        else:
            nodes = [Node.from_langchain(i) for i in nodes]
    elif isinstance(to_lion, Callable):
        nodes = _datanode_parser(nodes, to_lion)
    return nodes
