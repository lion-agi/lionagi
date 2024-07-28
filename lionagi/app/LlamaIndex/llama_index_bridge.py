class LlamaIndexBridge:

    @staticmethod
    def to_llama_index_node(*args, **kwargs):
        """
        Converts a Lion node to a Llama Index node of a specified type.

        This function takes a node from the Lion framework, converts it to a dictionary, modifies keys to match
        the expected Llama Index node schema, and then creates a Llama Index node object of the specified type.

        Args:
                lion_node: The Lion node to convert. Must have a `to_dict` method.
                node_type (Any, optional): The type of Llama Index node to create. Can be a string name of a node class
                        within the Llama Index schema or a class that inherits from `BaseNode`. Defaults to 'TextNode'.
                **kwargs: Additional keyword arguments to be included in the Llama Index node's initialization.

        Returns:
                Any: A new instance of the specified Llama Index node type populated with data from the Lion node.

        Raises:
                TypeError: If `node_type` is neither a string nor a subclass of `BaseNode`.
                AttributeError: If an error occurs due to an invalid node type or during the creation of the node object.
        """
        from .textnode import to_llama_index_node

        return to_llama_index_node(*args, **kwargs)

    @staticmethod
    def llama_index_read_data(*args, **kwargs):
        """
        Reads data using a specified llama index reader and its arguments.

        This function initializes a llama index reader with the given arguments and keyword arguments,
        then loads data using the reader's `load_data` method with the provided loader arguments and keyword arguments.

        Args:
                reader (Union[None, str, Any], optional): The reader to use. This can be a class, a string identifier,
                        or None. If None, a default reader is used.
                reader_args (List[Any], optional): Positional arguments to initialize the reader.
                reader_kwargs (Dict[str, Any], optional): Keyword arguments to initialize the reader.
                loader_args (List[Any], optional): Positional arguments for the reader's `load_data` method.
                loader_kwargs (Dict[str, Any], optional): Keyword arguments for the reader's `load_data` method.

        Returns:
                Any: The documents or data loaded by the reader.

        Raises:
                ValueError: If there is an error initializing the reader or loading the data.
        """
        from .reader import llama_index_read_data

        return llama_index_read_data(*args, **kwargs)

    @staticmethod
    def llama_index_parse_node(*args, **kwargs):
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
        from .node_parser import llama_index_parse_node

        return llama_index_parse_node(*args, **kwargs)

    @staticmethod
    def get_llama_index_reader(*args, **kwargs):
        """
        Retrieves a llama index reader object based on the specified reader name or class.

        This function checks if the specified reader is a recognized type or name and returns the appropriate
        llama index reader class. If a string is provided, it attempts to match it with known reader names and import
        the corresponding reader class dynamically. If a reader class is provided, it validates that the class is a
        subclass of BasePydanticReader.

        Args:
          reader (Union[Any, str], optional): The reader identifier, which can be a reader class, a string alias
                  for a reader class, or None. If None, returns the SimpleDirectoryReader class.

        Returns:
          Any: The llama index reader class corresponding to the specified reader.

        Raises:
          TypeError: If the reader is neither a string nor a subclass of BasePydanticReader.
          ValueError: If the specified reader string does not correspond to a known reader.
          AttributeError: If there is an issue importing the specified reader.
        """
        from .reader import get_llama_index_reader

        return get_llama_index_reader(*args, **kwargs)

    @staticmethod
    def index(nodes, **kwargs):
        from .index import LlamaIndex

        return LlamaIndex.index(nodes, **kwargs)
