# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.libs.utils import is_same_dtype

from ..typing.pydantic_ import (
    ConfigDict,
    Field,
    FieldInfo,
    PydanticUndefined,
    field_serializer,
    field_validator,
)
from ..typing.typing_ import UNDEFINED, Any, TypeVar, override
from .base import BaseAutoModel, common_config
from .field_model import FieldModel

FIELD_NAME = TypeVar("FIELD_NAME", bound=str)


class OperableModel(BaseAutoModel):
    """Model class supporting dynamic field management and operations.

    Provides:
    - Dynamic field addition/updates
    - Field attribute access
    - Metadata tracking
    - Nested model serialization

    Example:
        ```python
        class DynamicModel(OperableModel):
            base_field: str = "base"

        model = DynamicModel()

        # Add field with validation
        def validate_positive(v: int) -> int:
            if v <= 0:
                raise ValueError("Must be positive")
            return v

        model.add_field(
            "age",
            value=25,
            annotation=int,
            validator=validate_positive
        )
        ```

    Attributes:
        extra_fields: Dictionary storing dynamic field definitions
        model_config: Configuration forbidding extra direct fields
    """

    model_config = ConfigDict(
        extra="forbid", validate_default=False, **common_config
    )

    extra_fields: dict[str, Any] = Field(default_factory=dict)

    @field_serializer("extra_fields")
    def _serialize_extra_fields(
        self,
        value: dict[str, FieldInfo],
    ) -> dict[str, Any]:
        """Serialize extra fields to dictionary format.

        Args:
            value: Dictionary of field name to FieldInfo mappings

        Returns:
            Dictionary of field name to value mappings,
            with nested models serialized
        """
        output_dict = {}
        for k in value.keys():
            k_value = self.__dict__.get(k)
            if isinstance(k_value, BaseAutoModel):
                k_value = k_value.to_dict()
            output_dict[k] = k_value
        return output_dict

    @field_validator("extra_fields")
    def _validate_extra_fields(
        cls,
        value: list[FieldModel] | dict[str, FieldModel | FieldInfo],
    ) -> dict[str, FieldInfo]:
        """Validate and convert extra fields to FieldInfo objects.

        Args:
            value: List of FieldModels or dict of field definitions

        Returns:
            Dictionary mapping field names to FieldInfo objects

        Raises:
            ValueError: If value format is invalid
        """
        out = {}
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, FieldModel):
                    out[k] = v.field_info
                elif isinstance(v, FieldInfo):
                    out[k] = v
            return out

        elif isinstance(value, list) and is_same_dtype(value, FieldModel):
            return {v.name: v.field_info for v in value}

        raise ValueError("Invalid extra_fields value")

    @override
    def __setattr__(self, field_name: str, value: Any) -> None:
        """Set attribute value with metadata tracking.

        This method prevents direct assignment to metadata and extra_fields,
        and tracks the last update time of modified fields.

        Args:
            field_name: Name of the field to set
            value: Value to set

        Raises:
            AttributeError: If attempting to directly assign to metadata or
                extra_fields
        """
        if field_name in self.extra_fields:
            object.__setattr__(self, field_name, value)
        else:
            super().__setattr__(field_name, value)

    @override
    def to_dict(self, clean: bool = False) -> dict:
        """Convert model to dictionary including extra fields.

        Args:
            clean: If True, exclude UNDEFINED values

        Returns:
            Dictionary containing all fields and their values
        """
        dict_ = self.model_dump()
        dict_.pop("extra_fields")
        dict_.update(self._serialize_extra_fields(self.extra_fields))
        if clean:
            for k, v in dict_.items():
                if v is UNDEFINED:
                    dict_.pop(k)
        return dict_

    @property
    def all_fields(self) -> dict[str, FieldInfo]:
        """Get all fields including model fields and extra fields.

        Returns:
            Dictionary mapping field names to FieldInfo objects,
            excluding the extra_fields field itself
        """
        a = {**self.model_fields, **self.extra_fields}
        a.pop("extra_fields", None)
        return a

    def add_field(
        self,
        field_name: FIELD_NAME,
        /,
        value: Any = UNDEFINED,
        annotation: type = UNDEFINED,
        field_obj: FieldInfo = UNDEFINED,
        field_model: FieldModel = UNDEFINED,
        **kwargs,
    ) -> None:
        """Add a new field to the model's extra fields.

        Args:
            field_name: Name of the field to add
            value: Field value
            annotation: Type annotation
            field_obj: Pre-configured FieldInfo object
            field_model: Pre-configured FieldModel object
            **kwargs: Additional field configuration

        Raises:
            ValueError: If field already exists or invalid configuration
        """
        if field_name in self.all_fields:
            raise ValueError(f"Field '{field_name}' already exists")

        self.update_field(
            field_name,
            value=value,
            annotation=annotation,
            field_obj=field_obj,
            field_model=field_model,
            **kwargs,
        )

    def update_field(
        self,
        field_name: FIELD_NAME,
        /,
        value: Any = UNDEFINED,
        annotation: type = UNDEFINED,
        field_obj: FieldInfo = UNDEFINED,
        field_model: FieldModel = UNDEFINED,
        **kwargs,
    ) -> None:
        """Update existing field or create new one.

        Args:
            field_name: Name of field to update
            value: New field value
            annotation: Type annotation
            field_obj: Pre-configured FieldInfo object
            field_model: Pre-configured FieldModel object
            **kwargs: Additional field configuration

        Raises:
            ValueError: If invalid configuration provided
        """
        if "default" in kwargs and "default_factory" in kwargs:
            raise ValueError(
                "Cannot provide both 'default' and 'default_factory'",
            )

        if field_obj and field_model:
            raise ValueError(
                "Cannot provide both 'field_obj' and 'field_model'",
            )

        # Handle field_obj
        if field_obj:
            if not isinstance(field_obj, FieldInfo):
                raise ValueError(
                    "Invalid field_obj, should be a pydantic FieldInfo object"
                )
            self.extra_fields[field_name] = field_obj

        if field_model:
            if not isinstance(field_model, FieldModel):
                raise ValueError(
                    "Invalid field_model, should be a FieldModel object"
                )
            self.extra_fields[field_name] = field_model.field_info

        # Handle kwargs
        if kwargs:
            if field_name in self.all_fields:  # existing field
                for k, v in kwargs.items():
                    self.field_setattr(field_name, k, v)
            else:
                self.extra_fields[field_name] = Field(**kwargs)

        # Handle no explicit defined field
        if not field_obj and not kwargs:
            if field_name not in self.all_fields:
                self.extra_fields[field_name] = Field()

        field_obj = self.all_fields[field_name]

        # Handle annotation
        if annotation is not None:
            field_obj.annotation = annotation
        if not field_obj.annotation:
            field_obj.annotation = Any

        # Handle value
        if value is UNDEFINED:
            if getattr(self, field_name, UNDEFINED) is not UNDEFINED:
                value = getattr(self, field_name)
            elif getattr(field_obj, "default") is not PydanticUndefined:
                value = field_obj.default
            elif getattr(field_obj, "default_factory"):
                value = field_obj.default_factory()

        setattr(self, field_name, value)

    def field_setattr(
        self,
        field_name: FIELD_NAME,
        attr: str,
        value: Any,
        /,
    ) -> None:
        """Set attribute value for a field.

        Args:
            field_name: Name of field to modify
            attr: Name of attribute to set
            value: Value to set

        Raises:
            KeyError: If field not found
        """
        all_fields = self.all_fields
        if field_name not in all_fields:
            raise KeyError(f"Field {field_name} not found in object fields.")
        field_obj = all_fields[field_name]
        if hasattr(field_obj, attr):
            setattr(field_obj, attr, value)
        else:
            if not isinstance(field_obj.json_schema_extra, dict):
                field_obj.json_schema_extra = {}
            field_obj.json_schema_extra[attr] = value

    def field_hasattr(
        self,
        field_name: FIELD_NAME,
        attr: str,
        /,
    ) -> bool:
        """Check if field has specific attribute.

        Args:
            field_name: Name of field to check
            attr: Name of attribute to check

        Returns:
            True if attribute exists, False otherwise

        Raises:
            KeyError: If field not found
        """
        all_fields = self.all_fields
        if field_name not in all_fields:
            raise KeyError(f"Field {field_name} not found in object fields.")
        field_obj = all_fields[field_name]
        if hasattr(field_obj, attr):
            return True
        elif isinstance(field_obj.json_schema_extra, dict):
            if field_name in field_obj.json_schema_extra:
                return True
        else:
            return False

    def field_getattr(
        self,
        field_name: FIELD_NAME,
        attr: str,
        default: Any = UNDEFINED,
        /,
    ) -> Any:
        """Get attribute value for a field.

        Args:
            field_name: Name of field to access
            attr: Name of attribute to get
            default: Default value if attribute not found

        Returns:
            Attribute value

        Raises:
            KeyError: If field not found
            AttributeError: If attribute not found and no default
        """
        all_fields = self.all_fields

        if field_name not in all_fields:
            raise KeyError(f"Field {field_name} not found in object fields.")

        if str(attr).strip("s").lower() == "annotation":
            return self.model_fields[field_name].annotation

        field_obj = all_fields[field_name]

        # Check fieldinfo attr
        value = getattr(field_obj, attr, UNDEFINED)
        if value is not UNDEFINED:
            return value
        else:
            if isinstance(field_obj.json_schema_extra, dict):
                value = field_obj.json_schema_extra.get(attr, UNDEFINED)
                if value is not UNDEFINED:
                    return value

        # Handle undefined attr
        if default is not UNDEFINED:
            return default
        else:
            raise AttributeError(
                f"field {field_name} has no attribute {attr}",
            )


__all__ = [
    "OperableModel",
    "FIELD_NAME",
]
