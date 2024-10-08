from collections.abc import Mapping
from typing import Any

from lionabc.exceptions import (
    LionOperationError,
    LionTypeError,
    LionValueError,
)
from lionfuncs import validate_mapping
from typing_extensions import override

from lion_core.rule.default_rules.choice import ChoiceRule


class MappingRule(ChoiceRule):
    @override
    async def check_value(self, value: dict, /) -> str:
        if not isinstance(value, Mapping):
            raise LionTypeError("Invalid mapping field type.")

        if self.keys:
            if (keys := set(value.keys())) != set(self.keys):
                raise LionValueError(
                    "Invalid mapping keys. Current keys "
                    f"{[keys]} != {self.keys}"
                )

    @override
    async def fix_value(self, value: Any):
        if isinstance(value, list) and len(value) == 1:
            value = value[0]

        try:
            return validate_mapping(value, self.keys, **self.validation_kwargs)
        except ValueError as e:
            raise LionOperationError(
                f"Failed to fix {value} into a mapping."
            ) from e
