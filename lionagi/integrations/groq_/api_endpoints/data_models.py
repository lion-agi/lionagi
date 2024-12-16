# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GroqEndpointRequestBody(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class GroqEndpointResponseBody(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class GroqEndpointQueryParam(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class GroqEndpointPathParam(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class GroqChatMessage(BaseModel):
    role: str = Field(description="The role of the message sender")
    content: str = Field(description="The content of the message")
    name: str | None = Field(
        default=None, description="Optional name for the message sender"
    )


class GroqChatCompletionRequest(GroqEndpointRequestBody):
    messages: list[GroqChatMessage] = Field(
        description="List of messages in the conversation"
    )
    model: str = Field(description="ID of the model to use")
    temperature: float | None = Field(
        default=1.0,
        description="Sampling temperature between 0 and 2",
        ge=0.0,
        le=2.0,
    )
    top_p: float | None = Field(
        default=1.0,
        description="Nucleus sampling threshold",
        ge=0.0,
        le=1.0,
    )
    n: int | None = Field(
        default=1,
        description="Number of completions to generate",
        ge=1,
    )
    stream: bool | None = Field(
        default=False,
        description="Whether to stream the response",
    )
    stop: str | list[str] | None = Field(
        default=None,
        description="Sequences where the API will stop generating",
    )
    max_tokens: int | None = Field(
        default=None,
        description="Maximum number of tokens to generate",
        ge=1,
    )
    presence_penalty: float | None = Field(
        default=0.0,
        description="Presence penalty",
        ge=-2.0,
        le=2.0,
    )
    frequency_penalty: float | None = Field(
        default=0.0,
        description="Frequency penalty",
        ge=-2.0,
        le=2.0,
    )
    logit_bias: dict[str, float] | None = Field(
        default=None,
        description="Modify token likelihoods",
    )
    user: str | None = Field(
        default=None,
        description="Unique identifier for the end user",
    )

    @model_validator(mode="after")
    def validate_messages(self):
        if not self.messages:
            raise ValueError("Messages list cannot be empty")

        # Validate roles
        valid_roles = {"system", "user", "assistant"}
        for msg in self.messages:
            if msg.role not in valid_roles:
                raise ValueError(
                    f"Invalid role: {msg.role}. Must be one of {valid_roles}"
                )

        return self


class GroqAudioRequest(GroqEndpointRequestBody):
    model: str = Field(description="ID of the model to use")
    file: str = Field(description="Audio file to process")
    language: str | None = Field(
        default=None,
        description="Language of the audio (ISO-639-1)",
    )
    prompt: str | None = Field(
        default=None,
        description="Text to guide the model",
    )
    response_format: str | None = Field(
        default="json",
        description="Response format (json, text, or verbose_json)",
    )
    temperature: float | None = Field(
        default=0,
        description="Sampling temperature",
        ge=0.0,
        le=1.0,
    )
    timestamp_granularities: list[str] | None = Field(
        default=["segment"],
        description="Timestamp granularities (word or segment)",
    )


class GroqChatCompletionResponse(GroqEndpointResponseBody):
    id: str = Field(description="Unique identifier for the completion")
    object: str = Field(description="Object type")
    created: int = Field(description="Unix timestamp of creation")
    model: str = Field(description="Model used")
    choices: list[dict] = Field(description="Generated completions")
    usage: dict = Field(description="Token usage information")
    system_fingerprint: str | None = Field(
        description="System fingerprint for deterministic results"
    )


class GroqAudioResponse(GroqEndpointResponseBody):
    text: str = Field(description="Transcribed or translated text")
    x_groq: dict = Field(description="Groq-specific metadata")


# Request model mapping for iModel
GROQ_REQUEST_MODELS = {
    "create_chat_completion": {
        "request_body": GroqChatCompletionRequest,
    },
    "create_transcription": {
        "request_body": GroqAudioRequest,
    },
    "create_translation": {
        "request_body": GroqAudioRequest,
    },
    "chat/completions": {
        "request_body": GroqChatCompletionRequest,
    },
    "audio/transcriptions": {
        "request_body": GroqAudioRequest,
    },
    "audio/translations": {
        "request_body": GroqAudioRequest,
    },
}
