import json
from typing import Any
from lionagi.os.sys_util import SysUtil
from lionagi.os.libs import to_dict
from lionagi.os.primitives import note


def load_llamaindex_vector_store(folder):
    files = ["default__vector_store", "docstore", "index_store"]
    paths = [f"{folder}/{file}.json" for file in files]

    notes = {}
    for idx, p in enumerate(paths):
        a = json.load(open(p))
        notes[files[idx]] = note(**a)

    doc_note = notes["docstore"]
    vec_note = notes["default__vector_store"]
    index_note = notes["index_store"]

    for i in index_note["index_store/data"].keys():
        cp = ["index_store/data", i, "__data__"]
        index_note[cp] = to_dict(index_note[cp])

    def _get_index_node_list(index_id_):
        cp = ["index_store/data", index_id_, "__data__", "nodes_dict"]
        try:
            index_note[cp] = to_dict(index_note[cp])
        except:
            raise Exception(f"Index {index_id_} not found")

        nodes_dict = index_note[cp]
        all_nodes = list(nodes_dict.keys())
        out = []

        for i in all_nodes:
            cp = ["docstore/data", i, "__data__"]
            doc_note[cp] = to_dict(doc_note[cp])
            dict_ = doc_note[cp]

            cp = ["embedding_dict", i]
            dict_["embedding"] = vec_note[cp]
            out.append(dict_)

        return out

    results = [_get_index_node_list(i) for i in index_note["index_store/data"].keys()]

    return results if len(results) > 1 else results[0]


def get_llama_index_loader(reader: Any | str = None, *args, **kwargs) -> Any:

    SimpleDirectoryReader = SysUtil.check_import(
        package_name="llama_index",
        module_name="core",
        import_name="SimpleDirectoryReader",
        pip_name="llama-index",
    )

    BasePydanticReader = SysUtil.import_module(
        package_name="llama_index",
        module_name="core.readers.base",
        import_name="BasePydanticReader",
    )

    if reader in [
        "SimpleDirectoryReader",
        SimpleDirectoryReader,
        "simple-directory-reader",
        "simple_directory_reader",
        "simple",
        "simple_reader",
        "simple-reader",
    ]:
        reader = SimpleDirectoryReader()
        loader = reader(*args, **kwargs)
        return loader

    if not isinstance(reader, str) and not issubclass(reader, BasePydanticReader):
        raise TypeError(f"reader must be a string or BasePydanticReader.")

    if isinstance(reader, str):
        package_name, pip_name = parse_reader_name(reader)
        if package_name == "" and pip_name == "":
            raise ValueError(
                f"{reader} is not found. Please directly input llama-index reader class "
                f"or check llama-index documentation for supported readers."
            )
        try:
            reader = SysUtil.check_import(
                package_name=package_name,
                import_name=reader,
                pip_name=pip_name,
            )
            reader = reader()
            loader = reader(*args, **kwargs)
            return loader

        except Exception as e:
            raise AttributeError(
                f"Failed to import/download {reader}, "
                f"please check llama-index documentation to download it "
                f"manually and input the reader object: {e}"
            )

    elif issubclass(reader, BasePydanticReader):
        loader = reader(*args, **kwargs)
        return loader


def parse_reader_name(reader_str):

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


def llamaindex_loader(
    reader=None,
    /,
    *args,
    reader_args=[],
    reader_kwargs={},
    **kwargs,
) -> Any:
    try:
        loader = get_llama_index_loader(reader, *reader_args, **reader_kwargs)
        documents = loader.load_data(*args, **kwargs)
        return documents
    except Exception as e:
        raise ValueError(f"Failed to read and load data. Error: {e}")
