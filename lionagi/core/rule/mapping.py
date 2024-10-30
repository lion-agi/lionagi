from collections.abc import Mapping
from typing import Any

from lionfuncs import to_dict, validate_mapping

from lionagi.core.rule.choice import ChoiceRule


class MappingRule(ChoiceRule):
    """
    Rule for validating that a value is a mapping (dictionary) with specific keys.

    Attributes:
        apply_type (str): The type of data to which the rule applies.
    """

    def __init__(self, apply_type="dict", **kwargs):
        super().__init__(apply_type=apply_type, **kwargs)

    async def validate(self, value: Any, *args, **kwargs) -> Any:
        """
        Validate that the value is a mapping with specific keys.

        Args:
            value (Any): The value to validate.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The validated value.

        Raises:
            ValueError: If the value is not a valid mapping or has incorrect keys.
        """
        if not isinstance(value, Mapping):
            raise ValueError("Invalid mapping field type.")

        if self.keys:
            if (keys := set(value.keys())) != set(self.keys):
                raise ValueError(
                    f"Invalid mapping keys. Current keys {[i for i in keys]} != {self.keys}"
                )
        return value

    async def perform_fix(self, value: Any, *args, **kwargs) -> Any:
        """
        Attempt to fix the value by converting it to a dict and validating its keys.

        Args:
            value (Any): The value to fix.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The fixed value.

        Raises:
            ValueError: If the value cannot be fixed.
        """
        if not isinstance(value, dict):
            try:
                value = to_dict(value)
            except Exception as e:
                raise ValueError("Invalid dict field type.") from e

        if self.keys:
            check_keys = set(value.keys())
            if check_keys != set(self.keys):
                try:
                    return validate_mapping(
                        value, keys=self.keys, handle_unmatched="force"
                    )
                except Exception as e:
                    raise ValueError("Invalid dict keys.") from e

        else:
            try:
                return to_dict(value, fuzzy_parse=True)
            except Exception as e:
                raise ValueError("Invalid dict keys.") from e

        return value
