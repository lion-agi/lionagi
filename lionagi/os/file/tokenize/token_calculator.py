from typing import Type, Callable


class BaseTokenCalculator:

    def __init__(self, tokenizer: Callable | Type, **kwargs):
        if isinstance(tokenizer, Type):
            tokenizer = tokenizer(**kwargs)
        self.tokenizer = tokenizer

    def update_tokenizer(self, tokenizer: Callable | Type, **kwargs):
        if isinstance(tokenizer, Type):
            tokenizer = tokenizer(**kwargs)
        self.tokenizer = tokenizer

    def calculate_token(self, payload, endpoint, **kwargs): ...

    def tokenize(self): ...
