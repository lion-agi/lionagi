from typing import Any
from functools import singledispatchmethod
from lionagi.app.TikToken.token_calculator import TikTokenCalculator
from .config import OPENAI_TIKTOKEN_EMBEDDING_CONFIG


class OpenAIEmbeddingTokenCalculator(TikTokenCalculator):
    config = OPENAI_TIKTOKEN_EMBEDDING_CONFIG

    @classmethod
    def calculate(cls, e_: list):
        return cls._calculate_embed_item(e_)

    @singledispatchmethod
    @classmethod
    def _calculate_embed_item(cls, e_: Any):
        try:
            e_ = str(e_)
            return cls._calculate_embed_item(e_)
        except:
            return 0

    @_calculate_embed_item.register(str)
    def _(cls, e_: str):
        return cls._calculate(e_)

    @_calculate_embed_item.register(list)
    def _(cls, e_: list):
        return sum(cls._calculate_embed_item(e) for e in e_)
