OPENAI_TIKTOKEN_CHAT_CONFIG = {
    "encoding_name": "cl100k_base",
    "model_name": None,
    "tokenizer": None,
}

OPENAI_TIKTOKEN_EMBEDDING_CONFIG = {
    "encoding_name": "cl100k_base",
    "model_name": None,
    "tokenizer": None,
}

GPT4O_IMAGE_PRICING = {
    "base_cost": 85,
    "low_detail": 0,
    "max_dimension": 2048,
    "min_side": 768,
    "square_size": 512,
    "square_cost": 170,
}

GPT4O_MINI_IMAGE_PRICING = {
    "base_cost": 2833,
    "low_detail": 0,
    "max_dimension": 2048,
    "min_side": 768,
    "square_size": 512,
    "square_cost": 5667,
}

IMAGE_PRICE_MAPPING = {
    "gpt-4o-mini": GPT4O_MINI_IMAGE_PRICING,
    "gpt-4o": GPT4O_IMAGE_PRICING,
}
