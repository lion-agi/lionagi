# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import Field, model_validator

from ...data_models import AnthropicEndpointRequestBody
from .message_models import Message


class AnthropicMessageRequestBody(AnthropicEndpointRequestBody):
    model: str = Field(
        description="The model to use for generating the response"
    )

    messages: list[Message] = Field(
        description="The messages to send to the model"
    )

    max_tokens: int = Field(
        default=8000,  # Default to Anthropic's max model response tokens
        description="The maximum number of tokens to generate before stopping",
    )

    metadata: dict | None = Field(
        None, description="An object describing metadata about the request"
    )

    stop_sequences: list[str] | None = Field(
        None,
        description="Custom text sequences that will cause the model to stop generating",
    )

    stream: bool | None = Field(
        False, description="Whether to stream the response back token by token"
    )

    system: str | None = Field(
        None,
        description="System prompt that helps define the behavior of the assistant",
    )

    temperature: float | None = Field(
        None,
        ge=0,
        le=1,
        description="Amount of randomness injected into the response",
    )

    top_k: int | None = Field(
        None,
        description="Number of most likely tokens to consider at each step",
    )

    top_p: float | None = Field(
        None,
        ge=0,
        le=1,
        description="Total probability mass of tokens to consider at each step",
    )

    @model_validator(mode="after")
    def validate_messages(self):
        if not self.messages:
            raise ValueError("Messages list cannot be empty")

        # Check for alternating user/assistant messages
        for i in range(1, len(self.messages)):
            if self.messages[i].role == self.messages[i - 1].role:
                raise ValueError(
                    "Messages must alternate between user and assistant roles"
                )

        return self
