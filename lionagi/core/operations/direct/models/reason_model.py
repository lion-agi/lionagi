import logging
from typing import Any

from lionfuncs import to_num, validate_str
from pydantic import BaseModel, Field, field_validator


class ReasonModel(BaseModel):
    title: str = Field(
        ...,
        title="Title",
        description="Provide a concise title summarizing the reason.",
    )
    content: str = Field(
        ...,
        title="Content",
        description=(
            "Provide a detailed explanation supporting the reason, including relevant "
            "information or context."
        ),
    )
    confidence_score: float | None = Field(
        None,
        description=(
            "Provide an objective numeric confidence score between 0 and 1 (with 3 "
            "decimal places) indicating how likely you successfully achieved the task "
            "according to user expectation. Interpret the score as:\n"
            "- **1**: Very confident in a good job.\n"
            "- **0**: Not confident at all.\n"
            "- **[0.8, 1]**: You can continue the path of reasoning if needed.\n"
            "- **[0.5, 0.8)**: Recheck your reasoning and consider reverting to a "
            "previous, more confident reasoning path.\n"
            "- **[0, 0.5)**: Stop because the reasoning is starting to be off track."
        ),
        examples=[0.821, 0.257, 0.923, 0.439],
        ge=0,
        le=1,
    )

    @field_validator("title", mode="before")
    def validate_title(cls, value: Any) -> str:
        return validate_str(value, "title")

    @field_validator("content", mode="before")
    def validate_content(cls, value: Any) -> str:
        return validate_str(value, "content")

    @field_validator("confidence_score", mode="before")
    def validate_confidence_score(cls, value: Any) -> float:
        try:
            return to_num(
                value,
                upper_bound=1,
                lower_bound=0,
                num_type=float,
                precision=3,
            )
        except Exception as e:
            logging.error(f"Failed to convert {value} to a number. Error: {e}")
            return 0.0


__all__ = ["ReasonModel"]
