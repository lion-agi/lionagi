from __future__ import annotations
from abc import ABC, abstractmethod
import logging

from typing import Type, Callable
from pydantic import BaseModel
import tiktoken

from lion_core.abc import BaseManager
from lionagi.os.file.tokenize.utils import tokenize
from lionagi.os.file.tokenize.special_tokens import disallowed_tokens


class TokenCalculator(ABC): ...


class TextTokenCalculator(TokenCalculator): ...


class ImageTokenCalculator(TokenCalculator): ...


class EmbeddingTokenCalculator(TokenCalculator): ...


class ProviderTokenCalculator(TokenCalculator): ...


# class TextTokenCalculator(TokenCalculator):
#     ...

#     # @classmethod
#     # def calculate(
#     #     cls,
#     #     s:str,
#     #     model_name: str = None,     # priority 3
#     #     encoding_name: str = None,  # priority 2
#     #     tokenizer: Callable = None, # priority 1
#     # ):

#     #     if callable(tokenizer):
#     #         try:
#     #             return tokenizer(s)
#     #         except Exception as e:
#     #             logging.error(f"Error in tokenizing text with custom tokenizer, {e}")

#     #     if not encoding_name:
#     #         if model_name:
#     #             encoding_name = tiktoken.encoding_for_model(model_name)
#     #         else:
#     #             encoding_name = "cl100k_base"

#     #     tokenizer = tiktoken.get_encoding(encoding_name).encode


# class ImageTokenCalculator(TokenCalculator):

#     func: Callable


# class TokenManager(BaseManager):

#     # for calculating tokens purpose only
#     default_minimum_tokens = 15


#     def __init__(self, text_calculator: Callable | Type | None = None, image_calculator):
#         if not tokenizer:
#             self.tokenizer = tokenize
#         if isinstance(tokenizer, Type):
#             tokenizer = tokenizer(**kwargs)
#         self.tokenizer = tokenizer

#     def update_tokenizer(self, tokenizer: Callable | Type, **kwargs):
#         if isinstance(tokenizer, Type):
#             tokenizer = tokenizer(**kwargs)
#         self.tokenizer = tokenizer

#     def calculate_token(self, payload, endpoint, **kwargs):
#         ...


# def _calculate_single_message_token():
#     ...


# def _calculate_chat_completion_token(
#     payload: dict,
#     encoding: tiktoken.Encoding,
#     image_calculator: TokenCalculator | type[TokenCalculator],
#     default_max_tokens: int = 15,
# ):
#     max_tokens = payload.get("max_tokens", default_max_tokens)
#     num_tokens = 0

#     for msg in payload.get("messages", []):
#         # every message follows <im_start>{role/name}\n{content}<im_end>\n
#         num_tokens += 4
#         _content = msg.get("content")

#         if isinstance(_content, str):
#             num_tokens += len(encoding.encode(_content))

#         elif isinstance(_content, list):
#             for _m in _content:
#                 if not isinstance(_m, dict):
#                     num_tokens += len(encoding.encode(str(_m)))
#                     continue
#                 else:
#                     if "text" in


#     ...
