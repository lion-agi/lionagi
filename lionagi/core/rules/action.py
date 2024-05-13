from enum import Enum

from lionagi.libs import ParseUtil
from lionagi.libs.ln_convert import to_list, to_dict
from .mapping import MappingRule


class ActionRequestKeys(Enum):
    FUNCTION = "function"
    ARGUMENTS = "arguments"


class ActionRequestRule(MappingRule):

    def __init__(self, apply_type="actionrequest", discard=None, **kwargs):
        super().__init__(apply_type=apply_type, keys=ActionRequestKeys, **kwargs)
        self.discard = discard or self.validation_kwargs.get("discard", False)

    async def validate(self, value):
        if isinstance(value, dict) and list(value.keys()) >= ["function", "arguments"]:
            return value
        raise ValueError(f"Invalid action request field: {value}")

    async def perform_fix(self, value):
        corrected = []
        if isinstance(value, str):
            value = ParseUtil.fuzzy_parse_json(value)

        try:
            value = to_list(value)
            for i in value:
                i = to_dict(i)
                if list(i.keys()) >= ["function", "arguments"]:
                    corrected.append(i)
                elif not self.discard:
                    raise ValueError(f"Invalid action field: {i}")
        except Exception as e:
            raise ValueError(f"Invalid action field: {e}") from e

        return corrected
