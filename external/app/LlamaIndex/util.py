llama_meta_fields = [
    "id_",
    "embedding",
    "excluded_embed_metadata_keys",
    "excluded_llm_metadata_keys",
    "relationships",
    "start_char_idx",
    "end_char_idx",
    "class_name",
    "text_template",
    "metadata_template",
    "metadata_seperator",
]


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
