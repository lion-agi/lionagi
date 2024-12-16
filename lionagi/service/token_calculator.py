from abc import abstractmethod

import tiktoken
from pydantic import BaseModel, Field, field_validator


class TokenCalculator(BaseModel):

    @abstractmethod
    def calculate(self, *args, **kwargs): ...


class TiktokenCalculator(TokenCalculator):
    encoding_name: str = Field(
        description="Encoding for converting text to tokens. "
        "Input encoding name or a specific OpenAI model",
        examples=["o200k_base", "gpt-4o"],
    )

    @field_validator("encoding_name")
    @classmethod
    def get_encoding_name(cls, value: str) -> str:
        try:
            enc = tiktoken.encoding_for_model(value)
            return enc.name
        except:
            try:
                tiktoken.get_encoding(value)
                return value
            except:
                return "o200k_base"

    def encode(self, text: str) -> list[int]:
        enc = tiktoken.get_encoding(self.encoding_name)
        return enc.encode(text=text)

    def calculate(self, text: str) -> int:
        enc_text = self.encode(text)
        return len(enc_text)

    def tokenize(
        self, text: str, decode_byte_str: bool = False, decoder: str = "utf-8"
    ):
        enc = tiktoken.get_encoding(self.encoding_name)
        enc_text = self.encode(text)
        tokens = [
            enc.decode_single_token_bytes(token_id) for token_id in enc_text
        ]
        if decode_byte_str:
            tokens = [token.decode(decoder) for token in tokens]
        return tokens
