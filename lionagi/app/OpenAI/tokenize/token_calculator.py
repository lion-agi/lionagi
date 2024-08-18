from typing import Any
from lionagi.os.file.tokenize.token_calculator import ProviderTokenCalculator
from .chat_calculator import OpenAIChatTokenCalculator
from .embedding import OpenAIEmbeddingTokenCalculator


class OpenAITokenCalculator(ProviderTokenCalculator):

    chat_calculator = OpenAIChatTokenCalculator
    embedding_calculator = OpenAIEmbeddingTokenCalculator
    image_calculator = OpenAIChatTokenCalculator.image_calculator

    @classmethod
    def calculate(
        cls,
        endpoint: str = None,
        payload: dict = None,
        image_base64=None,
        image_detail=None,
    ):
        if image_base64:
            return cls.calculate_image(image_base64, image_detail)

        match endpoint:
            case "chat/completions":
                return cls.calculate_chat(payload["messages"])
            case "embeddings":
                return cls.calculate_embeddings(payload["input"])
            case _:
                raise ValueError(f"Invalid endpoint: {endpoint}")

    @classmethod
    def calculate_chat(cls, messages: list):
        return cls.chat_calculator.calculate(messages)

    @classmethod
    def calculate_embeddings(cls, e_: Any):
        return cls.embedding_calculator.calculate(e_)

    @classmethod
    def calculate_image(cls, i_: str, image_detail=None):
        return cls.image_calculator.calculate(i_, image_detail)

    def __getitem__(self, endpoint: str = "chat/completions"):
        match endpoint:
            case "chat/completions":
                return self.chat_calculator
            case "embeddings":
                return self.embedding_calculator
            case "images":
                return self.image_calculator
            case _:
                raise ValueError(f"Invalid endpoint: {endpoint}")
