from .gpt4o import GPT4O_MODEL_CONFIG
from .gpt4o_mini import GPT4O_MINI_MODEL_CONFIG
from .gpt4_turbo import GPT4_TURBO_MODEL_CONFIG
from .text_embeddings3_large import TEXT_EMBEDDINGS3_LARGE_MODEL_CONFIG
from .text_embeddings3_small import TEXT_EMBEDDINGS3_SMALL_MODEL_CONFIG


OAI_MODEL_SPECIFICATIONS = {
    "gpt-4o": GPT4O_MODEL_CONFIG,
    "gpt-4o-mini": GPT4O_MINI_MODEL_CONFIG,
    "gpt-4-turbo": GPT4_TURBO_MODEL_CONFIG,
    "text-embeddings-3-large": TEXT_EMBEDDINGS3_LARGE_MODEL_CONFIG,
    "text-embeddings-3-small": TEXT_EMBEDDINGS3_SMALL_MODEL_CONFIG,
}
