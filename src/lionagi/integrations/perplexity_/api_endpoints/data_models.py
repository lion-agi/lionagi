from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PerplexityEndpointRequestBody(BaseModel):
    """Base class for all Perplexity API endpoint request bodies."""

    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class PerplexityEndpointResponseBody(BaseModel):
    """Base class for all Perplexity API endpoint response bodies."""

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class Usage(BaseModel):
    """Token usage information for a request."""

    prompt_tokens: int = Field(
        description="Number of tokens in the prompt.",
        ge=0,
    )
    completion_tokens: int = Field(
        description="Number of tokens in the completion.",
        ge=0,
    )
    total_tokens: int = Field(
        description="Total number of tokens used in the request.",
        ge=0,
    )

    model_config = ConfigDict(extra="forbid")


class Citation(BaseModel):
    """Citation information for a response."""

    url: str = Field(description="The URL of the cited source.")
    text: str | None = Field(
        default=None, description="The relevant text from the source."
    )
    title: str | None = Field(
        default=None, description="The title of the source."
    )
    year: int | None = Field(
        default=None, description="The year of publication.", ge=0
    )
    author: str | None = Field(
        default=None, description="The author of the source."
    )

    model_config = ConfigDict(extra="forbid")
