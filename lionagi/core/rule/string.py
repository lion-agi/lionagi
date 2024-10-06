from lionfuncs import to_str

from lionagi.core.rule.base import Rule


class StringRule(Rule):
    """
    Rule for validating and converting string values.

    Attributes:
        fields (list[str]): The list of fields to which the rule applies.
        apply_type (str): The type of data to which the rule applies.
    """

    fields: list[str] = ["reason", "prediction", "answer"]

    def __init__(self, apply_type="str", **kwargs):
        super().__init__(apply_type=apply_type, **kwargs)

    async def validate(self, value):
        """
        Validate that the value is a string.

        Args:
            value: The value to validate.

        Returns:
            str: The validated string value.

        Raises:
            ValueError: If the value is not a string or is an empty string.
        """
        if isinstance(value, str) or value == "":
            return value
        raise ValueError(f"Invalid string field type.")

    async def perform_fix(self, value):
        try:
            return to_str(value, **self.validation_kwargs)
        except Exception as e:
            raise ValueError(
                f"Failed to convert {value} into a string value"
            ) from e
