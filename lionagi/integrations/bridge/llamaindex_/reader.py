from typing import Any

from lionagi.libs.sys_util import SysUtil


def get_llama_index_reader(reader: Any | str = None) -> Any:
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

    SysUtil.check_import("llama_index", pip_name="llama-index")
    from llama_index.core import SimpleDirectoryReader
    from llama_index.core.readers.base import BasePydanticReader

    if reader in [
        "SimpleDirectoryReader",
        SimpleDirectoryReader,
        "simple-directory-reader",
        "simple_directory_reader",
        "simple",
        "simple_reader",
        "simple-reader",
    ]:
        return SimpleDirectoryReader

    if not isinstance(reader, str) and not issubclass(
        reader, BasePydanticReader
    ):
        raise TypeError(f"reader must be a string or BasePydanticReader.")

    if isinstance(reader, str):
        package_name, pip_name = parse_reader_name(reader)
        if package_name == "" and pip_name == "":
            raise ValueError(
                f"{reader} is not found. Please directly input llama-index reader class "
                f"or check llama-index documentation for supported readers."
            )

        try:
            SysUtil.check_import(package_name, pip_name=pip_name)
            reader = getattr(SysUtil.import_module(package_name), reader)
            return reader

        except Exception as e:
            raise AttributeError(
                f"Failed to import/download {reader}, "
                f"please check llama-index documentation to download it "
                f"manually and input the reader object: {e}"
            )

    elif issubclass(reader, BasePydanticReader):
        return reader


def parse_reader_name(reader_str):
    """
    Parses a reader name string into a package and pip name.

    Given a reader name string, this function maps it to the corresponding package name and pip name
    to facilitate dynamic import and installation if necessary.

    Args:
            reader_str (str): The name of the reader as a string.

    Returns:
            Tuple[str, str]: A tuple containing the package name and the pip name corresponding to the reader.
    """

    package_name = ""
    pip_name = ""

    if reader_str == "PsychicReader":
        package_name = "llama_index.readers.psychic"
        pip_name = "llama-index-readers-psychic"
    elif reader_str == "DeepLakeReader":
        package_name = "llama_index.readers.deeplake"
        pip_name = "llama-index-readers-deeplake"
    elif reader_str == "QdrantReader":
        package_name = "llama_index.readers.qdrant"
        pip_name = "llama-index-readers-qdrant"
    elif reader_str == "DiscordReader":
        package_name = "llama_index.readers.discord"
        pip_name = "llama-index-readers-discord"
    elif reader_str == "SimpleMongoReader":
        package_name = "llama_index.readers.mongodb"
        pip_name = "llama-index-readers-mongodb"
    elif reader_str == "ChromaReader":
        package_name = "llama_index.readers.chroma"
        pip_name = "llama-index-readers-chroma"
    elif reader_str == "MyScaleReader":
        package_name = "llama_index.readers.myscale"
        pip_name = "llama-index-readers-myscale"
    elif reader_str == "FaissReader":
        package_name = "llama_index.readers.faiss"
        pip_name = "llama-index-readers-faiss"
    elif reader_str == "ObsidianReader":
        package_name = "llama_index.readers.obsidian"
        pip_name = "llama-index-readers-obsidian"
    elif reader_str == "SlackReader":
        package_name = "llama_index.readers.slack"
        pip_name = "llama-index-readers-slack"
    elif reader_str == "SimpleWebPageReader":
        package_name = "llama_index.readers.web"
        pip_name = "llama-index-readers-web"
    elif reader_str == "PineconeReader":
        package_name = "llama_index.readers.pinecone"
        pip_name = "llama-index-readers-pinecone"
    elif reader_str == "PathwayReader":
        package_name = "llama_index.readers.pathway"
        pip_name = "llama-index-readers-pathway"
    elif reader_str == "MboxReader":
        package_name = "llama_index.readers.mbox"
        pip_name = "llama-index-readers-mbox"
    elif reader_str == "MilvusReader":
        package_name = "llama_index.readers.milvus"
        pip_name = "llama-index-readers-milvus"
    elif reader_str == "NotionPageReader":
        package_name = "llama_index.readers.notion"
        pip_name = "llama-index-readers-notion"
    elif reader_str == "GithubRepositoryReader":
        package_name = "llama_index.readers.github"
        pip_name = "llama-index-readers-github"
    elif reader_str == "GoogleDocsReader":
        package_name = "llama_index.readers.google"
        pip_name = "llama-index-readers-google"
    elif reader_str == "DatabaseReader":
        package_name = "llama_index.readers.database"
        pip_name = "llama-index-readers-database"
    elif reader_str == "TwitterTweetReader":
        package_name = "llama_index.readers.twitter"
        pip_name = "llama-index-readers-twitter"
    elif reader_str == "WeaviateReader":
        package_name = "llama_index.readers.weaviate"
        pip_name = "llama-index-readers-weaviate"
    elif reader_str == "PandasAIReader":
        package_name = "llama_index.readers.pandas_ai"
        pip_name = "llama-index-readers-pandas-ai"
    elif reader_str == "IntercomReader":
        package_name = "llama_index.readers.intercom"
        pip_name = "llama-index-readers-intercom"

    return package_name, pip_name


def llama_index_read_data(
    reader=None,
    reader_args=None,
    reader_kwargs=None,
    loader_args=None,
    loader_kwargs=None,
):
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
    try:
        reader_args = reader_args or []
        reader_kwargs = reader_kwargs or {}
        loader_args = loader_args or []
        loader_kwargs = loader_kwargs or {}

        reader = get_llama_index_reader(reader)

        loader = reader(*reader_args, **reader_kwargs)
        documents = loader.load_data(*loader_args, **loader_kwargs)
        return documents
    except Exception as e:
        raise ValueError(f"Failed to read and load data. Error: {e}")
