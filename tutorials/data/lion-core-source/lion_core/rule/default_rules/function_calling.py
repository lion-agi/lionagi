from lionabc.exceptions import LionOperationError
from lionfuncs import to_dict, to_list
from typing_extensions import override

from lion_core.rule.default_rules.mapping import MappingRule


class FunctionCallingRule(MappingRule):
    """
    Rule for validating and fixing action requests.

    Inherits from `MappingRule` and provides specific validation and fix logic
    for action requests.

    Attributes:
        discard (bool): Indicates whether to discard invalid action requests.
    """

    @property
    def discard(self):
        return self.info.get(["discard"], True)

    @override
    async def validate(self, value):
        """
        Validates the action request.

        Args:
            value (Any): The value of the action request.

        Returns:
            Any: The validated action request.

        Raises:
            ActionError: If the action request is invalid.
        """

        try:
            return await super().validate(value)
        except LionOperationError as e:
            raise LionOperationError("Invalid action request: ") from e

    # we do not attempt to fix the keys
    # because if the keys are wrong, action is not safe to operate, and
    # is meaningless
    @override
    async def fix_value(self, value):
        corrected = []
        if isinstance(value, str):
            value = to_dict(value, str_type="json", fuzzy_parse=True)

        try:
            value = to_list(value, flatten=True, dropna=True)
            for i in value:
                i = to_dict(i, **self.validation_kwargs)
                if list(i.keys()) >= ["function", "arguments"]:
                    corrected.append(i)
                elif not self.discard:
                    raise LionOperationError(f"Invalid action request: {i}")
        except Exception as e:
            raise LionOperationError("Invalid action field: ") from e

        return corrected
