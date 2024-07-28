def _langchain_reader(reader, reader_args, reader_kwargs, to_lion: bool | Callable):
    """
    Reads data using a Langchain reader.

    Args:
        reader (str | Callable): The reader function or its name.
        reader_args (list): Positional arguments for the reader function.
        reader_kwargs (dict): Keyword arguments for the reader function.
        to_lion (bool | Callable): Whether to convert the data to Node instances or a custom parser.

    Returns:
        pile: A pile of Node instances or custom parsed nodes.

    Example usage:
        >>> nodes = _langchain_reader('langchain_reader', ['arg1'], {'key': 'value'}, True)
    """
    nodes = LangchainBridge.langchain_loader(reader, reader_args, reader_kwargs)
    if isinstance(to_lion, bool) and to_lion is True:
        return pile([Node.from_langchain(i) for i in nodes])

    elif isinstance(to_lion, Callable):
        nodes = _datanode_parser(nodes, to_lion)
    return nodes
