# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from ..typing.pydantic_ import BaseModel
from ..typing.typing_ import UNDEFINED, Any, Self

common_config = {
    "populate_by_name": True,
    "arbitrary_types_allowed": True,
    "use_enum_values": True,
}


class BaseAutoModel(BaseModel):
    """Base model class with enhanced serialization capabilities.

    Extends Pydantic's BaseModel to provide:
    - Clean dictionary conversion with UNDEFINED handling
    - Nested model serialization
    - Hash generation based on model content
    - Validation rules

    Example:
        ```python
        class User(BaseAutoModel):
            name: str = Field(min_length=2)
            age: int | None = None
            settings: dict = Field(default_factory=dict)

        user = User(name="John", age=30)
        data = user.to_dict(clean=True)  # Excludes UNDEFINED values
        ```

    Attributes:
        model_config: Default configuration for all instances
            - validate_default: True to validate default values
            - populate_by_name: True to allow field population by alias
            - arbitrary_types_allowed: True to allow any type
            - use_enum_values: True to use enum values in serialization
    """

    def to_dict(self, clean: bool = False) -> dict[str, Any]:
        """Convert model to dictionary, with optional cleaning.

        Args:
            clean: If True, exclude UNDEFINED values from output.
                  If False, include all fields using model_dump().

        Returns:
            Dictionary representation of model with nested models serialized
        """
        if not clean:
            return self.model_dump()
        return {
            k: v
            for k, v in self.model_dump(exclude_unset=True).items()
            if v is not UNDEFINED
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create model instance from dictionary data.

        Args:
            data: Dictionary containing field values

        Returns:
            New model instance

        Raises:
            ValueError: If required fields are missing or validation fails
        """
        return cls.model_validate(data)

    def __hash__(self) -> int:
        """Generate hash based on model's clean dictionary representation.

        Returns:
            Hash value that uniquely identifies the model's content
        """
        return hash(str(self.to_dict(True)))


__all__ = ["BaseAutoModel"]
