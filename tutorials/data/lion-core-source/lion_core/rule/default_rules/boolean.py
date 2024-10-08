from lionabc.exceptions import LionOperationError
from lionfuncs import validate_boolean
from typing_extensions import override

from lion_core.rule.base import Rule


class BooleanRule(Rule):
    """
    Rule for validating that a value is a boolean.

    Attributes:
        apply_type (str): The type of data to which the rule applies.
    """

    @override
    async def check_value(self, value, /) -> bool:
        if isinstance(value, bool):
            return value
        raise ValueError("Invalid boolean value.")

    @override
    async def fix_value(self, value) -> bool:
        try:
            return validate_boolean(value)
        except ValueError as e:
            raise LionOperationError("Failed to validate field: ") from e
