from typing import Any
from lionagi.os.file.tokenize.token_calculator import ProviderTokenCalculator
from .chat_calculator import OpenAIChatTokenCalculator
from .embedding import OpenAIEmbeddingTokenCalculator


class OpenAITokenCalculator(ProviderTokenCalculator):

    chat_calculator = OpenAIChatTokenCalculator
    embedding_calculator = OpenAIEmbeddingTokenCalculator
    image_calculator = OpenAIChatTokenCalculator.image_calculator

    @classmethod
    def calculate(cls, endpoint: str = None, payload: dict = None, image_base64=None):
        if image_base64:
            return cls.calculate_image(image_base64)

        match endpoint:
            case "chat/completions":
                return cls.calculate_chat(payload["messages"])
            case "embeddings":
                return cls.calculate_embedding(payload["input"])
            case _:
                raise ValueError(f"Invalid endpoint: {endpoint}")

    @classmethod
    def calculate_chat(cls, messages: list):
        return cls.chat_calculator.calculate(messages)

    @classmethod
    def calculate_embedding(cls, e_: Any):
        return cls.embedding_calculator.calculate(e_)

    @classmethod
    def calculate_image(cls, i_: str):
        return cls.image_calculator.calculate(i_)
