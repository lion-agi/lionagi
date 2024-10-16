import logging
from typing import Any

from lionfuncs import to_dict, to_num, validate_str
from pydantic import BaseModel, Field, field_validator


class ReasonModel(BaseModel):

    title: str | None = None
    content: str | None = None
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


class ActionRequestModel(BaseModel):

    function: str | None = Field(
        None,
        title="Function",
        description=(
            "Specify the name of the function to execute. **Choose from the provided "
            "`tool_schema`; do not invent function names.**"
        ),
        examples=["print", "add", "len"],
    )
    arguments: dict[str, Any] = Field(
        {},
        title="Arguments",
        description=(
            "Provide the arguments to pass to the function as a dictionary. **Use "
            "argument names and types as specified in the `tool_schema`; do not "
            "invent argument names.**"
        ),
        examples=[{"num1": 1, "num2": 2}, {"x": "hello", "y": "world"}],
    )

    @field_validator("function", mode="before")
    def validate_function(cls, value: Any) -> str:
        return validate_str(value, "function")

    @field_validator("arguments", mode="before")
    def validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            suppress=True,
            recursive=True,
        )


class ActionResponseModel(BaseModel):

    function: str
    arguments: dict[str, Any]
    response: Any
