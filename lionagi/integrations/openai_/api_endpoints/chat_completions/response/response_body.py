from typing import List, Literal, Optional

from pydantic import Field

from ...data_models import OpenAIEndpointResponseBody
from .choice_models import Choice, ChunkChoice
from .usage_models import Usage


class OpenAIChatCompletionResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(description="A unique identifier for the chat completion.")

    choices: list[Choice] = Field(
        description=(
            "A list of chat completion choices. Can be more than one if n "
            "is greater than 1."
        )
    )

    created: int = Field(
        description=(
            "The Unix timestamp (in seconds) of when the chat completion "
            "was created."
        )
    )

    model: str = Field(description="The model used for the chat completion.")

    service_tier: str | None = Field(
        None,
        description=(
            "The service tier used for processing the request. This field is "
            "only included if the service_tier parameter is specified in the "
            "request."
        ),
    )

    system_fingerprint: str = Field(
        description=(
            "This fingerprint represents the backend configuration that the "
            "model runs with. Can be used in conjunction with the seed "
            "request parameter to understand when backend changes have been "
            "made that might impact determinism."
        )
    )

    object: Literal["chat.completion"] = Field(
        description="The object type, which is always chat.completion."
    )

    usage: Usage = Field(
        description="Usage statistics for the completion request."
    )


class OpenAIChatCompletionChunkResponseBody(OpenAIEndpointResponseBody):
    id: str = Field(description="A unique identifier for the chat completion.")

    choices: list[ChunkChoice] = Field(
        description=(
            "A list of chat completion choices. Can be more than one if n "
            "is greater than 1."
        )
    )

    created: int = Field(
        description=(
            "The Unix timestamp (in seconds) of when the chat completion "
            "was created."
        )
    )

    model: str = Field(description="The model used for the chat completion.")

    service_tier: str | None = Field(
        None,
        description=(
            "The service tier used for processing the request. This field is "
            "only included if the service_tier parameter is specified in the "
            "request."
        ),
    )

    system_fingerprint: str = Field(
        description=(
            "This fingerprint represents the backend configuration that the "
            "model runs with. Can be used in conjunction with the seed "
            "request parameter to understand when backend changes have been "
            "made that might impact determinism."
        )
    )

    object: Literal["chat.completion.chunk"] = Field(
        description="The object type, which is always chat.completion."
    )

    usage: Usage | None = Field(
        None, description="Usage statistics for the completion request."
    )
