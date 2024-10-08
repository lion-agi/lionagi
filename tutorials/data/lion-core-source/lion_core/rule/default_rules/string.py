from typing import override

from lionfuncs import to_str

from lion_core.rule.base import Rule


class StringRule(Rule):
    """
    Rule for validating and converting string values.

    Attributes:
        fields (list[str]): The list of fields to which the rule applies.
        apply_type (str): The type of data to which the rule applies.
    """

    @override
    async def check_value(self, value):
        if not isinstance(value, str):
            raise ValueError("Invalid string field type.")

    @override
    async def fix_value(self, value):
        """
        Attempt to convert a value to a string.

        Args:
            value: The value to convert to a string.

        Returns:
            str: The value converted to a string.

        Raises:
            ValueError: If the value cannot be converted to a string.
        """
        try:
            return to_str(value, **self.validation_kwargs)
        except Exception as e:
            value = (
                str(value)[30] + ".." if len(str(value)) > 30 else str(value)
            )
            raise ValueError(
                f"Failed to convert {value} into a string value"
            ) from e
