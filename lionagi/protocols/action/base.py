from lionagi.core.models.types import FieldModel

from .utils import (
    validate_action_required,
    validate_arguments,
    validate_function_name,
)

function_field_description = (
    "Name of the function to call from the provided `tool_schemas`. "
    "If no `tool_schemas` exist, set to None or leave blank. "
    "Never invent new function names outside what's given."
)

arguments_field_description = (
    "Dictionary of arguments for the chosen function. "
    "Use only argument names/types defined in `tool_schemas`. "
    "Never introduce extra argument names."
)

action_required_field_description = (
    "Whether this step strictly requires performing actions. "
    "If true, the requests in `action_requests` must be fulfilled, "
    "assuming `tool_schemas` are available. "
    "If false or no `tool_schemas` exist, actions are optional."
)

action_requests_field_description = (
    "List of actions to be executed when `action_required` is true. "
    "Each action must align with the available `tool_schemas`. "
    "Leave empty if no actions are needed."
)

__all__ = (
    "FUNCTION_FIELD",
    "ARGUMENTS_FIELD",
    "ACTION_REQUIRED_FIELD",
    "ACTION_REQUESTS_FIELD",
)


FUNCTION_FIELD = FieldModel(
    name="function",
    default=None,
    annotation=str | None,
    title="Function",
    description=function_field_description,
    examples=["add", "multiply", "divide"],
    validator=validate_function_name,
)

ARGUMENTS_FIELD = FieldModel(
    name="arguments",
    annotation=dict | None,
    default_factory=dict,
    title="Action Arguments",
    description=arguments_field_description,
    examples=[{"num1": 1, "num2": 2}, {"x": "hello", "y": "world"}],
    validator=validate_arguments,
    validator_kwargs={"mode": "before"},
)

ACTION_REQUIRED_FIELD = FieldModel(
    name="action_required",
    annotation=bool,
    default=False,
    title="Action Required",
    description=action_required_field_description,
    validator=validate_action_required,
    validator_kwargs={"mode": "before"},
)
