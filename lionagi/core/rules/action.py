from lionagi.core.generic.abc import ActionError
from enum import Enum

from lionagi.libs import ParseUtil
from lionagi.libs.ln_convert import to_list, to_dict
from .mapping import MappingRule


class ActionRequestKeys(Enum):
    FUNCTION = "function"
    ARGUMENTS = "arguments"


class ActionRequestRule(MappingRule):

    def __init__(self, apply_type="actionrequest", discard=None, **kwargs):
        super().__init__(
            apply_type=apply_type, keys=ActionRequestKeys, fix=True, **kwargs
        )
        self.discard = discard or self.validation_kwargs.get("discard", False)

    async def validate(self, value):
        if isinstance(value, dict) and list(value.keys()) >= ["function", "arguments"]:
            return value
        raise ActionError(f"Invalid action request: {value}")

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
                    raise ActionError(f"Invalid action request: {i}")
        except Exception as e:
            raise ActionError(f"Invalid action field: ") from e

        return corrected
