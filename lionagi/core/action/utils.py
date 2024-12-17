import re
from typing import Any, TypeAlias, TypeVar

from pydantic import BaseModel

from lionagi.libs.parse.types import fuzzy_parse_json, to_json

# Type aliases
JsonDict: TypeAlias = dict[str, Any]
ValidatorType = TypeVar("ValidatorType")
ActionList: TypeAlias = list[JsonDict]


def parse_action_request_model(
    content: str | JsonDict | BaseModel,
) -> ActionList:
    """Parse action request from various input formats."""

    json_blocks = []

    if isinstance(content, BaseModel):
        json_blocks = [content.model_dump()]

    elif isinstance(content, str):
        json_blocks = to_json(content, fuzzy_parse=True)
        if not json_blocks:
            pattern2 = r"```python\s*(.*?)\s*```"
            _d = re.findall(pattern2, content, re.DOTALL)
            json_blocks = []
            for match in _d:
                if a := fuzzy_parse_json(match):
                    json_blocks.append(a)

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
                    j["arguments"] = fuzzy_parse_json(v)
            if (
                j
                and all(key in j for key in ["function", "arguments"])
                and j["arguments"]
            ):
                out.append(j)

    return out
