# https://api.openai.com/v1/embeddings

embedding_llmconfig = {
    "model": "text-embedding-3-small",
    "encoding_format": "float", 
    "dimensions": None,
    "user": None,
}

embedding_schema = {
    "required": ["model"],
    "optional": [
        "encoding_format",
        "dimensions",
        "user",
    ],
    "input_": "input",
    "config": embedding_llmconfig,
}
