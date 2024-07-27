from functools import singledispatchmethod
from lion_core.libs import nget

from lionagi.app.TikToken.token_calculator import TikTokenCalculator
from .image import OpenAIImageTokenCalculator
from .config import OPENAI_TIKTOKEN_CHAT_CONFIG


class OpenAIChatTokenCalculator(TikTokenCalculator):

    image_calculator = OpenAIImageTokenCalculator
    config = OPENAI_TIKTOKEN_CHAT_CONFIG

    @classmethod
    def calculate(cls, messages: list):
        num_tokens = 0
        for msg in messages:
            num_tokens += 4
            _c = msg.get("content")
            num_tokens += cls._calculate_chatitem(_c)
        return num_tokens + 15  # buffer for chat

    @singledispatchmethod
    @classmethod
    def _calculate_chatitem(
        cls,
        i_=None,
    ):
        try:
            i_ = str(i_)
            return cls._calculate_chatitem(i_)
        except:
            return 0

    @_calculate_chatitem.register(str)
    @classmethod
    def _(cls, i_: str):
        return cls._calculate(i_)

    @_calculate_chatitem.register(dict)
    @classmethod
    def _(cls, i_: dict):
        if "text" in i_:
            return cls._calculate_chatitem(str(i_["text"]))
        elif "image_url" in i_:
            a: str = nget(["image_url", "url"], i_)
            if "data:image/jpeg;base64," in a:
                a = a.split("data:image/jpeg;base64,")[1].strip()
            return (
                cls.image_calculator.calculate(a, nget(["detail"], i_, "low")) + 15
            )  # buffer for image
        return 0

    @_calculate_chatitem.register(list)
    @classmethod
    def _(cls, i_: list):
        return sum(cls._calculate_chatitem(i) for i in i_)
