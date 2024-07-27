from .gpt4o import GPT4O
from .gpt4o_mini import GPT4O_MINI
from .gpt4_turbo import GPT4_TURBO
from .gpt35_turbo import GPT35_TURBO
from .gpt35_turbo_instruct import GPT35_TURBO_INSTRUCT
from .text_embeddings3_small import TEXT_EMBEDDINGS3_SMALL
from .text_embeddings3_large import TEXT_EMBEDDINGS3_LARGE


OPENAI_MODEL_MAPPING = {
    "gpt-4o": GPT4O,
    "gpt-4o-mini": GPT4O_MINI,
    "gpt-4-turbo": GPT4_TURBO,
    "gpt-3.5-turbo": GPT35_TURBO,
    "gpt-3.5-turbo-instruct": GPT35_TURBO_INSTRUCT,
    "text-embeddings-3-small": TEXT_EMBEDDINGS3_SMALL,
    "text-embeddings-3-large": TEXT_EMBEDDINGS3_LARGE,
}

__all__ = ["OPENAI_MODEL_MAPPING"]
