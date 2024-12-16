# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from ..typing.pydantic_ import ConfigDict
from .base import BaseAutoModel, common_config


class SchemaModel(BaseAutoModel):
    """Schema definition model with strict validation.

    Extends BaseAutoModel to provide:
    - Extra field forbidding
    - Disabled default validation
    - Field name listing
    - Nested validation

    Example:
        ```python
        class UserSchema(SchemaModel):
            name: str = Field(min_length=2)
            age: int = Field(gt=0)
            settings: dict[str, Any] = Field(default_factory=dict)

        # Raises error - extra fields forbidden
        user = UserSchema(name="John", age=30, extra="value")
        ```

    Attributes:
        model_config: Schema-specific configuration
            - extra: "forbid" to prevent extra fields
            - validate_default: False to skip default validation
            - Plus inherited BaseAutoModel config
    """

    model_config = ConfigDict(
        extra="forbid", validate_default=False, **common_config
    )

    @classmethod
    def keys(cls) -> list[str]:
        """Get list of model field names.

        Returns:
            List of field names defined in model schema
        """
        return list(cls.model_fields.keys())


__all__ = ["SchemaModel"]
