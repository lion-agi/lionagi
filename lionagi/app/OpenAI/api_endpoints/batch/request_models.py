from typing import Dict, Any, List, Union
from pydantic import Field, field_validator
from .base_models import OpenAIBaseModel
from .types import MethodLiteral, EndpointLiteral, RoleLiteral, ModelNameType


class Message(OpenAIBaseModel):
    role: RoleLiteral = Field(
        ..., description="The role of the message author.", example="user"
    )
    content: str = Field(
        ..., description="The content of the message.", example="Hello, how are you?"
    )


class ChatCompletionRequest(OpenAIBaseModel):
    model: ModelNameType = Field(
        ...,
        description="The model to use for chat completion.",
        example="gpt-3.5-turbo",
    )
    messages: List[Message] = Field(
        ...,
        description="The list of messages in the conversation.",
        example=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
        ],
    )
    temperature: float = Field(
        1.0, description="Controls randomness in the output.", example=0.7
    )
    top_p: float = Field(1.0, description="Controls diversity via nucleus sampling.")
    n: int = Field(1, description="How many chat completion choices to generate.")
    stream: bool = Field(False, description="Whether to stream partial progress.")
    stop: Union[str, List[str], None] = Field(
        None, description="Up to 4 sequences where the API will stop generating."
    )
    max_tokens: int = Field(
        1024, description="The maximum number of tokens to generate."
    )
    presence_penalty: float = Field(
        0.0,
        description="Penalizes new tokens based on their presence in the text so far.",
    )
    frequency_penalty: float = Field(
        0.0,
        description="Penalizes new tokens based on their frequency in the text so far.",
    )


class CompletionRequest(OpenAIBaseModel):
    model: ModelNameType = Field(
        ..., description="The model to use for completion.", example="gpt-3.5-turbo"
    )
    prompt: Union[str, List[str]] = Field(
        ...,
        description="The prompt(s) to generate completions for.",
        example="Translate the following English text to French: 'Hello, how are you?'",
    )
    temperature: float = Field(1.0, description="Controls randomness in the output.")
    top_p: float = Field(1.0, description="Controls diversity via nucleus sampling.")
    n: int = Field(1, description="How many completion choices to generate.")
    stream: bool = Field(False, description="Whether to stream partial progress.")
    stop: Union[str, List[str], None] = Field(
        None, description="Up to 4 sequences where the API will stop generating."
    )
    max_tokens: int = Field(
        1024, description="The maximum number of tokens to generate.", example=60
    )
    presence_penalty: float = Field(
        0.0,
        description="Penalizes new tokens based on their presence in the text so far.",
    )
    frequency_penalty: float = Field(
        0.0,
        description="Penalizes new tokens based on their frequency in the text so far.",
    )


class EmbeddingRequest(OpenAIBaseModel):
    model: ModelNameType = Field(
        ..., description="The model to use for embedding.", example="gpt-3.5-turbo"
    )
    input: Union[str, List[str]] = Field(
        ...,
        description="The input text to get embeddings for.",
        example="The food was delicious and the waiter...",
    )


class RequestInputObject(OpenAIBaseModel):
    custom_id: str = Field(
        ..., description="A custom identifier for the request.", example="request-1"
    )
    method: MethodLiteral = Field(
        ..., description="The HTTP method for the request.", example="POST"
    )
    url: EndpointLiteral = Field(
        ..., description="The API endpoint URL.", example="/v1/chat/completions"
    )
    body: Dict[str, Any] = Field(
        ...,
        description="The request body.",
        example={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is 2+2?"},
            ],
        },
    )

    @field_validator("body")
    def validate_body(cls, v: Dict[str, Any], info: Dict[str, Any]) -> Dict[str, Any]:
        url = info.data.get("url")
        if url == "/v1/chat/completions":
            if "messages" not in v:
                raise ValueError("'messages' is required for chat completions")
        elif url == "/v1/completions":
            if "prompt" not in v:
                raise ValueError("'prompt' is required for completions")
        elif url == "/v1/embeddings":
            if "input" not in v:
                raise ValueError("'input' is required for embeddings")
        return v
