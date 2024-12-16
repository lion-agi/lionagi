from pydantic import BaseModel, ConfigDict, Field, field_validator

from lionagi.integrations.perplexity_.api_endpoints.data_models import (
    PerplexityEndpointRequestBody,
)


class Message(BaseModel):
    """A message in the chat completion request."""

    role: str = Field(description="The role of the message author.")
    content: str = Field(description="The content of the message.")

    model_config = ConfigDict(extra="forbid")

    @field_validator("role")
    @classmethod
    def validate_role(cls, role: str) -> str:
        valid_roles = ["system", "user", "assistant"]
        if role not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")
        return role

    @field_validator("content")
    @classmethod
    def validate_content(cls, content: str) -> str:
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        return content


class PerplexityChatCompletionRequestBody(PerplexityEndpointRequestBody):
    """Request body for chat completion requests."""

    model: str = Field(description="ID of the model to use.")
    messages: list[Message] = Field(
        description="A list of messages comprising the conversation so far."
    )
    max_tokens: int | None = Field(
        default=None,
        description="The maximum number of tokens to generate in the completion.",
        ge=1,
    )
    temperature: float | None = Field(
        default=0.2,
        description="What sampling temperature to use, between 0 and 2.",
        ge=0,
        lt=2,
    )
    top_p: float | None = Field(
        default=0.9,
        description="An alternative to sampling with temperature, called nucleus sampling.",
        ge=0,
        le=1,
    )
    search_domain_filter: list[str] | None = Field(
        default=None,
        description="List of domains to limit citations to.",
    )
    return_images: bool | None = Field(
        default=False,
        description="Whether to return images in the response.",
    )
    return_related_questions: bool | None = Field(
        default=False,
        description="Whether to return related questions in the response.",
    )
    search_recency_filter: str | None = Field(
        default=None,
        description="Filter for search results recency (month, week, day, hour).",
    )
    top_k: int | None = Field(
        default=0,
        description="The number of tokens to keep for highest top-k filtering.",
        ge=0,
        le=2048,
    )
    stream: bool | None = Field(
        default=False,
        description="Whether to stream back partial progress.",
    )
    presence_penalty: float | None = Field(
        default=0,
        description="Penalty for new tokens based on their presence in text so far.",
        ge=-2,
        le=2,
    )
    frequency_penalty: float | None = Field(
        default=1,
        description="Penalty for new tokens based on their frequency in text so far.",
        gt=0,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("search_recency_filter")
    @classmethod
    def validate_search_recency_filter(cls, value: str | None) -> str | None:
        if value is not None:
            valid_filters = ["month", "week", "day", "hour"]
            if value not in valid_filters:
                raise ValueError(
                    f"Search recency filter must be one of {valid_filters}"
                )
        return value

    @field_validator("search_domain_filter")
    @classmethod
    def validate_search_domain_filter(
        cls, value: list[str] | None
    ) -> list[str] | None:
        if value is not None and len(value) > 3:
            raise ValueError("Search domain filter is limited to 3 domains")
        return value

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, messages: list[Message]) -> list[Message]:
        if not messages:
            raise ValueError("At least one message is required")
        return messages
