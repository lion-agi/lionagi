import warnings
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator
from typing_extensions import deprecated

#
# 1) CONTENT PART MODELS
#


class TextContentPart(BaseModel):
    """Represents a piece of text content."""

    type: Literal["text"]
    text: str


class RefusalContentPart(BaseModel):
    """Represents a refusal message from the model."""

    type: Literal["refusal"]
    refusal: str


class ImageUrl(BaseModel):
    """Contains either a direct URL or base64-encoded image data."""

    url: str
    detail: str | None = None  # 'auto' by default, or 'low', 'high'


class ImageContentPart(BaseModel):
    """Represents an image content part."""

    type: Literal["image"]
    image_url: ImageUrl


class AudioData(BaseModel):
    """Represents base64-encoded audio data and its format."""

    data: str
    format: Literal["wav", "mp3"]


class AudioContentPart(BaseModel):
    """Represents an audio content part (input audio)."""

    type: Literal["input_audio"]
    input_audio: AudioData


ContentPart = (
    TextContentPart | RefusalContentPart | ImageContentPart | AudioContentPart
)


class FunctionToCall(BaseModel):
    """Specifies the function name and arguments the model wants to call."""

    name: str
    arguments: str  # The JSON-encoded arguments


class ToolCall(BaseModel):
    """Represents a single tool call by the model."""

    id: str
    type: Literal["function"]  # Currently only 'function' is supported
    function: FunctionToCall


class ChatMessage(BaseModel):
    """
    Generic schema for any message in the 'messages' list:
      - role must be one of developer, system, user, assistant, tool, function (deprecated)
      - content can be a string or a list of content parts.
      - Additional optional fields are included if relevant for that role.
    """

    role: Literal[
        "developer", "system", "user", "assistant", "tool", "function"
    ]
    name: str | None = None
    content: str | list[ContentPart] | None = None
    tool_calls: list[ToolCall] | None = None

    function_call: FunctionToCall | None = Field(
        None,
        deprecated=deprecated(
            "`function_call` in OpenAI chat completions ChatMessage has been deprecated. "
            "Use 'tool_calls' instead."
        ),
    )

    audio: dict[str, Any] | None = (
        None  # If the assistant responded with audio previously
    )
    refusal: str | None = None

    # For 'tool' role messages:
    tool_call_id: str | None = None

    @field_validator("role", mode="before")
    def _validate_deprecated_roles(cls, value):
        if value == "function":
            warnings.warn(
                "The 'function' role is deprecated. Please use 'tool' instead.",
                DeprecationWarning,
            )
        return value


class ToolDefinitionFunction(BaseModel):
    """One function tool definition the model may call."""

    name: str
    description: str | None = None
    parameters: dict[str, Any] | None = None


class ToolDefinition(BaseModel):
    """Represents a tool that might be called by the model (e.g., a function)."""

    type: Literal["function"]
    name: str
    description: str | None = None
    parameters: dict[str, Any] | None = None


class OpenAIChatCompletionRequest(BaseModel):
    """
    The main Pydantic model for creating an OpenAI Chat Completion request.
    Includes both standard and advanced fields (some of which may be model-specific or deprecated).
    """

    model: str = Field(
        ..., description="ID of the model to use (e.g. gpt-4o)."
    )

    messages: list[ChatMessage] = Field(
        ...,
        description="A list of messages comprising the conversation so far.",
    )

    # Optional fields
    store: bool | None = False
    reasoning_effort: Literal["low", "medium", "high"] | None = (
        None  # for o1 models
    )
    metadata: dict[str, Any] | None = None

    frequency_penalty: float | None = 0
    logit_bias: dict[str, float] | None = None
    logprobs: bool | None = False
    top_logprobs: int | None = None

    # Deprecated in favor of max_completion_tokens
    max_tokens: int | None = None

    max_completion_tokens: int | None = None
    n: int | None = 1

    # E.g. ["text"], or ["text", "audio"] for gpt-4o-audio-preview
    modalities: list[str] | None = None

    # Audio object if you're requesting audio output, etc.
    prediction: dict[str, Any] = None
    presence_penalty: float | None = 0

    response_format: dict[str, Any] | None = None
    seed: int | None = None
    service_tier: Literal["auto", "default"] | None = "auto"
    stop: str | list[str] | None = None
    stream: bool | None = False

    # Streaming-specific options
    stream_options: dict[str, Any] | None = None

    temperature: float | None = 1
    top_p: float | None = 1

    # Tools / functions the model may call
    tools: list[ToolDefinition] | None = None
    tool_choice: (
        Literal["none", "auto", "required"] | dict[str, Any] | None
    ) = None
    parallel_tool_calls: bool | None = True

    # If you want to track user, for moderation or analytics
    user: str | None = None

    # Deprecated in favor of tool_choice
    function_call: str | dict[str, str] | None = Field(
        None,
        deprecated=deprecated(
            "`function_call` in OpenAI chat/completions endpoint has been deprecated. Use 'tools' instead."
        ),
    )
    functions: list[ToolDefinitionFunction] | None = None

    class Config:
        schema_extra = {
            "example": {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "developer",
                        "content": "You are a helpful assistant.",
                    },
                    {"role": "user", "content": "Hello!"},
                ],
                "stream": False,
                "max_completion_tokens": 1000,
                "temperature": 0.8,
                "top_p": 1,
                "tools": [
                    {
                        "type": "function",
                        "name": "lookupWeather",
                        "description": "Returns weather info for a location.",
                        "parameters": {
                            "type": "object",
                            "properties": {"location": {"type": "string"}},
                            "required": ["location"],
                        },
                    }
                ],
            }
        }
