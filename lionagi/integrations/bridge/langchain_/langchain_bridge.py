class LangchainBridge:

    @staticmethod
    def to_langchain_document(*args, **kwargs):
        """
        Converts a generic data node into a Langchain Document.

        This function transforms a node, typically from another data schema, into a Langchain Document format.
        It requires the source node to have a `to_dict` method to convert it into a dictionary, then it renames specific keys
        to match the Langchain Document schema before creating a Langchain Document object.

        Args:
                datanode (T): The data node to convert. Must have a `to_dict` method.
                **kwargs: Additional keyword arguments to be passed to the Langchain Document constructor.

        Returns:
                Any: An instance of `LangchainDocument` populated with data from the input node.
        """
        from .documents import to_langchain_document

        return to_langchain_document(*args, **kwargs)

    @staticmethod
    def langchain_loader(*args, **kwargs):
        """
        Initializes and uses a specified loader to load data within the Langchain ecosystem.

        This function supports dynamically selecting a loader by name or directly using a loader function.
        It passes specified arguments and keyword arguments to the loader for data retrieval or processing.

        Args:
                loader (Union[str, Callable]): A string representing the loader's name or a callable loader function.
                loader_args (List[Any], optional): A list of positional arguments for the loader.
                loader_kwargs (Dict[str, Any], optional): A dictionary of keyword arguments for the loader.

        Returns:
                Any: The result returned by the loader function, typically data loaded into a specified format.

        Raises:
                ValueError: If the loader cannot be initialized or fails to load data.
        """
        from .documents import langchain_loader

        return langchain_loader(*args, **kwargs)

    @staticmethod
    def langchain_text_splitter(*args, **kwargs):
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
        from .documents import langchain_text_splitter

        return langchain_text_splitter(*args, **kwargs)
