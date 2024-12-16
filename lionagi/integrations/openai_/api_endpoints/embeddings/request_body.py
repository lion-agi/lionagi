from typing import List, Literal, Optional, Union

from pydantic import ConfigDict, Field, model_validator

from ..data_models import OpenAIEndpointRequestBody

InputType = Union[str, list[str], list[int], list[list[int]]]
EncodingFormat = Literal["float", "base64"]


class OpenAIEmbeddingRequestBody(OpenAIEndpointRequestBody):
    input: InputType = Field(
        description=(
            "Input text to embed, encoded as a string or array of tokens. "
            "To embed multiple inputs in a single request, pass an array of "
            "strings or array of token arrays. The input must not exceed "
            "the max input tokens for the model (8192 tokens for "
            "text-embedding-ada-002), cannot be an empty string, and any "
            "array must be 2048 dimensions or less."
        ),
    )

    model: str = Field(
        description=(
            "ID of the model to use. You can use the List models API to see "
            "all of your available models, or see our Model overview for "
            "descriptions of them."
        ),
    )

    encoding_format: EncodingFormat | None = Field(
        "float",
        description=(
            "The format to return the embeddings in. Can be either `float` "
            "or `base64`."
        ),
    )

    dimensions: int | None = Field(
        None,
        description=(
            "The number of dimensions the resulting output embeddings "
            "should have. Only supported in `text-embedding-3` and later "
            "models."
        ),
    )

    user: str | None = Field(
        None,
        description=(
            "A unique identifier representing your end-user, which can help "
            "OpenAI to monitor and detect abuse."
        ),
    )

    @model_validator(mode="after")
    def validate_input(self) -> "OpenAIEmbeddingRequestBody":
        if isinstance(self.input, str) and self.input.strip() == "":
            raise ValueError("Input cannot be an empty string.")
        if isinstance(self.input, list):
            if len(self.input) == 0:
                raise ValueError("Input array cannot be empty.")
            if isinstance(self.input[0], list) and len(self.input) > 2048:
                raise ValueError(
                    "Input array must be 2048 dimensions or less."
                )
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "input": "The food was delicious and the waiter...",
                "model": "text-embedding-ada-002",
                "encoding_format": "float",
                "dimensions": None,
                "user": "user123",
            }
        }
    )
