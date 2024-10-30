from typing import Any

from lionfuncs import to_num

from lionagi.core.rule.base import Rule


class NumberRule(Rule):
    """
    Rule for validating that a value is a number within specified bounds.

    Attributes:
        apply_type (str): The type of data to which the rule applies.
        upper_bound (int | float | None): The upper bound for the value.
        lower_bound (int | float | None): The lower bound for the value.
        num_type (Type[int | float]): The type of number (int or float).
        precision (int | None): The precision for floating point numbers.
    """

    fields: list[str] = ["confidence_score", "score"]

    def __init__(self, apply_type="int, float", **kwargs):
        super().__init__(apply_type=apply_type, **kwargs)
        self.upper_bound = self.validation_kwargs.get("upper_bound")
        self.lower_bound = self.validation_kwargs.get("lower_bound")
        self.num_type = self.validation_kwargs.get("num_type", float)
        self.precision = self.validation_kwargs.get("precision")

    async def validate(self, value: Any) -> Any:
        """
        Validate that the value is a number.

        Args:
            value (Any): The value to validate.

        Returns:
            Any: The validated value.

        Raises:
            ValueError: If the value is not a valid number.
        """
        if isinstance(value, (int, float)):
            return value
        raise ValueError(f"Invalid number field: {value}")

    async def perform_fix(self, value: Any) -> Any:
        """
        Attempt to fix the value by converting it to a number.

        Args:
            value (Any): The value to fix.

        Returns:
            Any: The fixed value.

        Raises:
            ValueError: If the value cannot be converted to a number.
        """
        if isinstance(value, (int, float)):
            return value

        value = to_num(
            value,
            **{
                k: v
                for k, v in self.validation_kwargs.items()
                if k in ["num_type", "precision", "upper_bound", "lower_bound"]
            },
        )

        if isinstance(value, (int, float)):
            return value
        raise ValueError(f"Failed to convert {value} into a numeric value")
