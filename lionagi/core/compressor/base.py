from abc import ABC, abstractmethod
from ..collections import iModel


class TokenCompressor(ABC):

    def __init__(self, imodel: iModel, tokenizer=None, splitter=None):
        self.imodel = imodel
        self.tokenizer = tokenizer
        self.splitter = splitter

    @abstractmethod
    def tokenize(self, text):
        pass

    @abstractmethod
    def split(self, text):
        pass

    @abstractmethod
    async def compress(self, text, **kwargs):
        pass
