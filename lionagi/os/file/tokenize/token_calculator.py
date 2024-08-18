import logging
from abc import ABC, abstractmethod
from lion_core.abc import AbstractObserver


class TokenCalculator(AbstractObserver):

    config = {}

    @abstractmethod
    def calculate(self, *args, **kwargs): ...


class TextTokenCalculator(TokenCalculator):

    def __init__(self, **kwargs):
        super().__init__()
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        self.config = {**self.config, **kwargs}

    def update_config(self, **kwargs):
        self.config = {**self.config, **kwargs}

    @abstractmethod
    def tokenize(self, *args, **kwargs): ...

    @property
    def disallowed_tokens(self):
        return self.config.get("disallowed_tokens", [])

    @disallowed_tokens.setter
    def disallowed_tokens(self, value):
        self.config["disallowed_tokens"] = value

    @property
    def encoding_name(self):
        return self.config.get("encoding_name", None)

    @encoding_name.setter
    def encoding_name(self, value):
        self.config["encoding_name"] = value

    @property
    def model_name(self):
        return self.config.get("model_name", None)

    @model_name.setter
    def model_name(self, value):
        self.config["model_name"] = value

    @property
    def tokenizer(self):
        return self.config.get("tokenizer", self.tokenize)

    @tokenizer.setter
    def tokenizer(self, value):
        self.config["tokenizer"] = value


class ImageTokenCalculator(TokenCalculator): ...


class EmbeddingTokenCalculator(TextTokenCalculator): ...


class ProviderTokenCalculator(TokenCalculator):

    def __getitem__(self, endpoint: str = "chat/completions"):
        raise NotImplementedError("ProviderTokenCalculator is an abstract class.")
