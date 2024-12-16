import re

from lionagi.core.typing import (
    Any,
    BaseModel,
    Field,
    FieldModel,
    field_validator,
)
from lionagi.libs.parse import to_dict, to_json, validate_boolean

from .prompts import (
    action_requests_field_description,
    action_required_field_description,
    arguments_field_description,
    function_field_description,
)


def parse_action_request(content: str | dict) -> list[dict]:

    json_blocks = []

    if isinstance(content, BaseModel):
        json_blocks = [content.model_dump()]

    elif isinstance(content, str):
        json_blocks = to_json(content, fuzzy_parse=True)
        print(json_blocks)
        if not json_blocks:
            pattern2 = r"```python\s*(.*?)\s*```"
            _d = re.findall(pattern2, content, re.DOTALL)
            json_blocks = [to_dict(match, fuzzy_parse=True) for match in _d]
            json_blocks = [i for i in json_blocks if i]

    elif content and isinstance(content, dict):
        json_blocks = [content]

    if json_blocks and not isinstance(json_blocks, list):
        json_blocks = [json_blocks]

    out = []

    for i in json_blocks:
        print(i)
        j = {}
        if isinstance(i, dict):
            if "function" in i and isinstance(i["function"], dict):
                if "name" in i["function"]:
                    i = i["function"]
            for k, v in i.items():
                k = (
                    k.replace("action_", "")
                    .replace("recipient_", "")
                    .replace("s", "")
                )
                if k in ["name", "function", "recipient"]:
                    j["function"] = v
                elif k in ["parameter", "argument", "arg"]:
                    j["arguments"] = to_dict(
                        v, str_type="json", fuzzy_parse=True, suppress=True
                    )
            if (
                j
                and all(key in j for key in ["function", "arguments"])
                and j["arguments"]
            ):
                out.append(j)

    return out


def _validate_function_name(cls, value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return value


def _validate_action_required(cls, value) -> bool:
    try:
        return validate_boolean(value)
    except Exception:
        return False


def _validate_arguments(cls, value: Any) -> dict:
    return to_dict(
        value,
        fuzzy_parse=True,
        suppress=True,
        recursive=True,
    )


FUNCTION_FIELD = FieldModel(
    name="function",
    default=None,
    annotation=str | None,
    title="Function",
    description=function_field_description,
    examples=["add", "multiply", "divide"],
    validator=_validate_function_name,
)

ARGUMENTS_FIELD = FieldModel(
    name="arguments",
    annotation=dict | None,
    default_factory=dict,
    title="Action Arguments",
    description=arguments_field_description,
    examples=[{"num1": 1, "num2": 2}, {"x": "hello", "y": "world"}],
    validator=_validate_arguments,
    validator_kwargs={"mode": "before"},
)

ACTION_REQUIRED_FIELD = FieldModel(
    name="action_required",
    annotation=bool,
    default=False,
    title="Action Required",
    description=action_required_field_description,
    validator=_validate_action_required,
    validator_kwargs={"mode": "before"},
)


class ActionRequestModel(BaseModel):

    function: str | None = FUNCTION_FIELD.field_info
    arguments: dict[str, Any] | None = ARGUMENTS_FIELD.field_info

    @field_validator("arguments", mode="before")
    def validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            recursive=True,
            recursive_python_only=False,
        )

    @classmethod
    def create(cls, content: str):
        try:
            content = parse_action_request(content)
            if content:
                return [cls.model_validate(i) for i in content]
            return []
        except Exception:
            return []


class ActionResponseModel(BaseModel):

    function: str = Field(default_factory=str)
    arguments: dict[str, Any] = Field(default_factory=dict)
    output: Any = None


ACTION_REQUESTS_FIELD = FieldModel(
    name="action_requests",
    annotation=list[ActionRequestModel],
    default_factory=list,
    title="Actions",
    description=action_requests_field_description,
)


ACTION_RESPONSES_FIELD = FieldModel(
    name="action_responses",
    annotation=list[ActionResponseModel],
    default_factory=list,
    title="Actions",
    description="**do not fill**",
)

__all__ = [
    "ActionRequestModel",
    "ActionResponseModel",
    "ACTION_REQUESTS_FIELD",
    "ACTION_RESPONSES_FIELD",
]
