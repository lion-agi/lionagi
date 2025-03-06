from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class PerplexityRole(str, Enum):
    """Roles allowed in Perplexity's messages."""

    system = "system"
    user = "user"
    assistant = "assistant"


class PerplexityMessage(BaseModel):
    """
    A single message in the conversation.
    `role` can be 'system', 'user', or 'assistant'.
    `content` is the text for that conversation turn.
    """

    role: PerplexityRole = Field(
        ...,
        description="The role of the speaker. Must be system, user, or assistant.",
    )
    content: str = Field(..., description="The text content of this message.")


class PerplexityChatCompletionRequest(BaseModel):
    """
    Represents the request body for Perplexity's Chat Completions endpoint.
    Endpoint: POST https://api.perplexity.ai/chat/completions
    """

    model: str = Field(
        "sonar",
        description="The model name, e.g. 'sonar', (the only model available at the time when this request model was updated, check doc for latest info).",
    )
    messages: list[PerplexityMessage] = Field(
        ..., description="A list of messages forming the conversation so far."
    )

    # Optional parameters
    frequency_penalty: float | None = Field(
        default=None,
        gt=0,
        description=(
            "Multiplicative penalty > 0. Values > 1.0 penalize repeated tokens more strongly. "
            "Value=1.0 means no penalty. Incompatible with presence_penalty."
        ),
    )
    presence_penalty: float | None = Field(
        default=None,
        ge=-2.0,
        le=2.0,
        description=(
            "Penalizes tokens that have appeared so far (range -2 to 2). "
            "Positive values encourage talking about new topics. Incompatible with frequency_penalty."
        ),
    )
    max_tokens: int | None = Field(
        default=None,
        description=(
            "Maximum number of completion tokens. If omitted, model generates tokens until it "
            "hits stop or context limit."
        ),
    )
    return_images: bool | None = Field(
        default=None,
        description="If True, attempt to return images (closed beta feature).",
    )
    return_related_questions: bool | None = Field(
        default=None,
        description="If True, attempt to return related questions (closed beta feature).",
    )
    search_domain_filter: list[Any] | None = Field(
        default=None,
        description=(
            "List of domains to limit or exclude in the online search. Example: ['example.com', '-twitter.com']. "
            "Supports up to 3 entries. (Closed beta feature.)"
        ),
    )
    search_recency_filter: str | None = Field(
        default=None,
        description=(
            "Returns search results within a specified time interval: 'month', 'week', 'day', or 'hour'."
        ),
    )
    stream: bool | None = Field(
        default=None,
        description=(
            "If True, response is returned incrementally via Server-Sent Events (SSE)."
        ),
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        lt=2.0,
        description=(
            "Controls randomness of sampling, range [0, 2). Higher => more random. "
            "Defaults to 0.2."
        ),
    )
    top_k: int | None = Field(
        default=None,
        ge=0,
        le=2048,
        description=(
            "Top-K filtering. 0 disables top-k filtering. If set, only the top K tokens are considered. "
            "We recommend altering either top_k or top_p, but not both."
        ),
    )
    top_p: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Nucleus sampling threshold. We recommend altering either top_k or top_p, but not both."
        ),
    )

    @model_validator(mode="before")
    def validate_penalties(cls, values):
        """
        Disallow using both frequency_penalty != 1.0 and presence_penalty != 0.0 at once,
        since the docs say they're incompatible.
        """
        freq_pen = values.get("frequency_penalty", 1.0)
        pres_pen = values.get("presence_penalty", 0.0)

        # The doc states frequency_penalty is incompatible with presence_penalty.
        # We'll enforce that if presence_penalty != 0, frequency_penalty must be 1.0
        # or vice versa. Adjust logic as needed.
        if pres_pen != 0.0 and freq_pen != 1.0:
            raise ValueError(
                "presence_penalty is incompatible with frequency_penalty. "
                "Please use only one: either presence_penalty=0 with freq_pen !=1, "
                "or presence_penalty!=0 with freq_pen=1."
            )
        return values

    def to_dict(self) -> dict:
        """Return a dict suitable for JSON serialization and sending to Perplexity API."""
        return self.model_dump(exclude_none=True)
