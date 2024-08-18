from functools import singledispatchmethod
from typing import Any

from lionagi.os.libs import nget
from lionagi.app.TikToken.token_calculator import TikTokenCalculator
from .image import OpenAIImageTokenCalculator
from .config import OPENAI_TIKTOKEN_CHAT_CONFIG, IMAGE_PRICE_MAPPING


class OpenAIChatTokenCalculator(TikTokenCalculator):

    image_calculator_class = OpenAIImageTokenCalculator
    image_calculator = None

    def __init__(self, model_name=None, config=None, image_config=None):
        super().__init__()
        self.config = config or OPENAI_TIKTOKEN_CHAT_CONFIG
        if model_name:
            self.config["model_name"] = model_name

        if self.image_calculator is None:
            image_config = image_config or IMAGE_PRICE_MAPPING.get(model_name, None)
            if image_config is not None:
                self.image_calculator = self.image_calculator_class(
                    config=image_config,
                )

    def calculate(self, messages: list):
        num_tokens = 0
        for msg in messages:
            num_tokens += 4
            _c = msg.get("content")
            num_tokens += self._calculate_chatitem(_c)
        return num_tokens  # buffer for chat

    @singledispatchmethod
    def _calculate_chatitem(self, i_: Any):
        try:
            i_ = str(i_)
            return self._calculate(i_)
        except:
            return 0

    @_calculate_chatitem.register(str)
    def _(self, i_: str):
        return self._calculate(
            i_,
            encoding_name=self.config["encoding_name"],
            model_name=self.config["model_name"],
        )

    @_calculate_chatitem.register(dict)
    def _(self, i_: dict):
        if "text" in i_:
            return self._calculate_chatitem(str(i_["text"]))
        elif "image_url" in i_:
            a: str = nget(["image_url", "url"], i_)
            if "data:image/jpeg;base64," in a:
                a = a.split("data:image/jpeg;base64,")[1].strip()
            return (
                self.image_calculator.calculate(
                    a,
                    nget(i_, ["detail"], "low"),
                )
                + 15
            )  # buffer for image
        return 0

    @_calculate_chatitem.register(list)
    def _(self, i_: list):
        return sum(self._calculate_chatitem(i) for i in i_)
