"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from enum import Enum
from lionagi.os.lib import to_list, to_dict, fuzzy_parse_json
from ..abc import ActionError
from .mapping import MappingRule


class ActionRequestKeys(Enum):
    FUNCTION = "function"
    ARGUMENTS = "arguments"


class ActionRequestRule(MappingRule):
    """
    Rule for validating and fixing action requests.

    Inherits from `MappingRule` and provides specific validation and fix logic
    for action requests.

    Attributes:
        discard (bool): Indicates whether to discard invalid action requests.
    """

    def __init__(self, apply_type="actionrequest", discard=True, **kwargs):
        """
        Initializes the ActionRequestRule.

        Args:
            apply_type (str): The type of data to which the rule applies.
            discard (bool, optional): Indicates whether to discard invalid action requests.
            **kwargs: Additional keyword arguments for initialization.
        """
        super().__init__(
            apply_type=apply_type, keys=ActionRequestKeys, fix=True, **kwargs
        )
        self.discard = discard or self.validation_kwargs.get("discard", False)

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
        if isinstance(value, dict) and list(value.keys()) >= ["function", "arguments"]:
            return value
        raise ActionError(f"Invalid action request: {value}")

    async def perform_fix(self, value):
        """
        Attempts to fix an invalid action request.

        Args:
            value (Any): The value of the action request to fix.

        Returns:
            Any: The fixed action request.

        Raises:
            ActionError: If the action request cannot be fixed.
        """
        corrected = []
        if isinstance(value, str):
            value = fuzzy_parse_json(value)

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
