from collections.abc import Mapping
from lionagi.libs.ln_convert import to_dict
from lionagi.libs import StringMatch

from .choice import ChoiceRule


class MappingRule(ChoiceRule):

    def __init__(self, apply_type="dict", **kwargs):
        super().__init__(apply_type, **kwargs)

    async def validate(self, value, *args, **kwargs):
        if not isinstance(value, Mapping):
            raise ValueError("Invalid mapping field type.")

        if (keys := set(value.keys())) != set(self.keys):
            raise ValueError(
                f"Invalid mapping keys. Current keys {[i for i in keys]} != {self.keys}"
            )
        return value

    async def perform_fix(self, value, *args, **kwargs):
        if not isinstance(value, dict):
            try:
                value = to_dict(value)
            except Exception as e:
                raise ValueError("Invalid dict field type.") from e

        check_keys = set(value.keys())
        if check_keys != set(self.keys):
            try:
                return StringMatch.force_validate_dict(value, keys=self.keys)
            except Exception as e:
                raise ValueError("Invalid dict keys.") from e
        return value
