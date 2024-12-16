from typing import List, Literal, Optional

from pydantic import Field

from ..data_models import OllamaEndpointRequestBody
from ..option_models import Option
from .message_models import Message
from .tool_models import Tool


class OllamaChatCompletionRequestBody(OllamaEndpointRequestBody):
    model: str = Field(description="The model name")

    messages: list[Message] = Field(
        description="The messages of the chat, this can be used to keep a chat memory"
    )

    tools: list[Tool] | None = Field(
        None,
        description="Tools for the model to use if supported. Requires 'stream' to be set to false",
    )

    format: Literal["json"] | None = Field(
        None,
        description="The format to return a response in. Currently the only accepted value is 'json'",
    )

    options: Option | None = Field(
        None,
        description="Additional model parameters listed in the documentation for the Modelfile",
    )

    stream: bool = Field(
        True,
        description="If false the response will be returned as a single response object, "
        "rather than a stream of objects",
    )

    keep_alive: str | Literal[0] = Field(
        "5m",
        description="Controls how long the model will stay loaded into memory following the request.",
    )
