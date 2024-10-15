import logging
from typing import Any

from lionfuncs import (
    MutableModel,
    to_dict,
    to_num,
    validate_boolean,
    validate_str,
)
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


REASON_FIELD: ReasonModel | None = Field(None)
ACTION_REQUESTS_FIELD: list[ActionRequestModel] = Field(
    [],
    title="Actions",
    description=(
        "List of actions to be performed if `action_required` is **True**. Leave "
        "empty if no action is required. **When providing actions, you must "
        "choose from the provided `tool_schema`. Do not invent function or "
        "argument names.**"
    ),
)

ACTION_RESPONSES_FIELD: list[ActionResponseModel] = []

ACTION_REQUIRED: bool = Field(
    False,
    title="Action Required",
    description=(
        "if there are no tool_schema provied, must mark as **False**. "
        "Indicate whether this step requires an action. Set to **True** if an "
        "action is required; otherwise, set to **False**."
    ),
)

RESPONSE: Any = None


class Operative(MutableModel):

    @field_validator("action_required", mode="before")
    def validate_action_required(cls, value: Any) -> bool:
        try:
            return validate_boolean(value)
        except Exception as e:
            logging.error(
                f"Failed to convert {value} to a boolean. Error: {e}"
            )
            return False

    @classmethod
    def get_request_response_model(
        cls, reason: bool = False, actions: bool = False
    ):
        return cls.as_request_model(reason, actions), cls.as_response_model(
            reason, actions
        )

    @classmethod
    def as_request_model(cls, reason: bool = False, actions: bool = False):
        if reason and actions:
            return cls.new_model(
                model_name="ReAct" + cls.__name__,
                reason=REASON_FIELD,
                actions=ACTION_REQUESTS_FIELD,
                action_required=ACTION_REQUIRED,
            )
        elif reason:
            return cls.new_model(
                model_name="Reason" + cls.__name__,
                reason=REASON_FIELD,
            )
        elif actions:
            return cls.new_model(
                model_name="Action" + cls.__name__,
                actions=ACTION_REQUESTS_FIELD,
                action_required=ACTION_REQUIRED,
            )
        return cls.new_model(model_name=cls.__name__)

    @classmethod
    def as_response_model(cls, reason: bool = False, actions: bool = False):
        if reason and actions:
            return cls.new_model(
                model_name="ReAct" + cls.__name__,
                reason=REASON_FIELD,
                actions=ACTION_RESPONSES_FIELD,
                action_required=ACTION_REQUIRED,
            )
        elif reason:
            return cls.new_model(
                model_name="Reason" + cls.__name__,
                reason=REASON_FIELD,
            )
        elif actions:
            return cls.new_model(
                model_name="Action" + cls.__name__,
                actions=ACTION_RESPONSES_FIELD,
                action_required=ACTION_REQUIRED,
            )
        return cls.new_model(model_name=cls.__name__)
