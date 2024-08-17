from __future__ import annotations
from abc import ABC, abstractmethod
from lion_core.abc import AbstractObserver


class TokenCalculator(AbstractObserver):

    @abstractmethod
    def calculate(self, *args, **kwargs): ...


class TextTokenCalculator(TokenCalculator):

    @abstractmethod
    def tokenize(self, *args, **kwargs): ...


class ImageTokenCalculator(TokenCalculator): ...


class EmbeddingTokenCalculator(TextTokenCalculator): ...


class ProviderTokenCalculator(TokenCalculator):

    def __getitem__(self, endpoint: str = "chat/completions"):
        raise NotImplementedError("ProviderTokenCalculator is an abstract class.")
