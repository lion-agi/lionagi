from abc import ABC
from lionagi.os.operator.imodel.imodel import iModel


class TokenCompressor(ABC):
    def __init__(self, imodel: iModel, tokenizer=None, splitter=None):
        self.imodel = imodel
        self.tokenizer = tokenizer
        self.splitter = splitter
