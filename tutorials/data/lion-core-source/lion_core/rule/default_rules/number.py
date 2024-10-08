from typing import Any

from lionabc.exceptions import LionTypeError
from lionfuncs import to_num
from typing_extensions import override

from lion_core.rule.base import Rule


class NumberRule(Rule):
    @override
    async def check_value(self, value: Any) -> Any:
        """
        Validate that the value is a number.

        Args:
            value (Any): The value to validate.

        Returns:
            Any: The validated value.

        Raises:
            ValueError: If the value is not a valid number.
        """
        if isinstance(value, int | float | complex):
            return value
        raise LionTypeError(f"Invalid number field type: {type(value)}")

    @override
    async def fix_value(self, value: Any) -> Any:
        """
        Attempt to fix the value by converting it to a number.

        Args:
            value (Any): The value to fix.

        Returns:
            Any: The fixed value.

        Raises:
            ValueError: If the value cannot be converted to a number.
        """
        return to_num(value, **self["validation_kwargs"])
