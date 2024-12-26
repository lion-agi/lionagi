import re

from lionagi.core.typing import Any, BaseModel
from lionagi.libs.parse import to_dict, to_json, validate_boolean


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


def validate_function_name(cls, value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return value


def validate_action_required(cls, value) -> bool:
    try:
        return validate_boolean(value)
    except Exception:
        return False


def validate_arguments(cls, value: Any) -> dict:
    return to_dict(
        value,
        fuzzy_parse=True,
        suppress=True,
        recursive=True,
    )
