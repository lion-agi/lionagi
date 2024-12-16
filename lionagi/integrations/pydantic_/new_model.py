# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


from collections.abc import Callable
from typing import Any, Literal, TypeVar, overload

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    create_model,
    field_validator,
)
from pydantic.fields import FieldInfo

T = TypeVar("T", bound=BaseModel)


@overload
def new_model(
    base: type[T],
    *,
    model_name: str | None = None,
    use_all_fields: Literal[False] = False,
    config_dict: ConfigDict | None = None,
    doc: str | None = None,
    validators: dict[str, Callable] | None = None,
    use_base_kwargs: bool = False,
    inherit_base: bool = False,
    extra_fields: dict[str, Any] | None = None,
    field_descriptions: dict[str, str] | None = None,
    exclude_fields: list[str] | None = None,
    frozen: bool = False,
) -> type[BaseModel]: ...


@overload
def new_model(
    base: type[T],
    *,
    model_name: str | None = None,
    use_all_fields: Literal[True],
    config_dict: ConfigDict | None = None,
    doc: str | None = None,
    validators: dict[str, Callable] | None = None,
    use_base_kwargs: bool = False,
    inherit_base: bool = False,
    extra_fields: dict[str, Any] | None = None,
    field_descriptions: dict[str, str] | None = None,
    exclude_fields: list[str] | None = None,
    frozen: bool = False,
) -> type[BaseModel]: ...


def new_model(
    base: type[T] | T,
    *,
    model_name: str | None = None,
    use_all_fields: bool = False,
    config_dict: ConfigDict | None = None,
    doc: str | None = None,
    validators: dict[str, Callable] | None = None,
    use_base_kwargs: bool = False,
    inherit_base: bool = False,
    extra_fields: dict[str, Any] | None = None,
    field_descriptions: dict[str, str] | None = None,
    exclude_fields: list[str] | None = None,
    frozen: bool = False,
) -> type[BaseModel]:
    """
    Create a new Pydantic model based on an existing model with additional customizations.

    This function allows you to create a new Pydantic model by extending or modifying
    an existing model. It provides various options to customize the new model's fields,
    configuration, and behavior.

    Args:
        base: The base model or instance to derive the new model from.
        model_name: Name for the new model. Defaults to f"Dynamic{base.__name__}".
        use_all_fields: If True, includes fields from base.all_fields (if available).
        config_dict: Additional configuration options for the model.
        doc: Docstring for the new model.
        validators: Dictionary of field validators to add to the model.
        use_base_kwargs: If True, includes class kwargs from the base model.
        inherit_base: If True, sets the base model as the parent class.
        extra_fields: Additional fields to add to the new model.
        field_descriptions: Dictionary of field descriptions to add or update.
        exclude_fields: List of field names to exclude from the new model.
        frozen: If True, creates an immutable model.

    Returns:
        A new Pydantic model class.

    Raises:
        ValueError: If invalid arguments are provided.

    Examples:
        >>> class BaseUser(BaseModel):
        ...     name: str
        ...     age: int
        >>> NewUser = new_model(
        ...     BaseUser,
        ...     model_name="ExtendedUser",
        ...     extra_fields={"email": (str, ...)},
        ...     field_descriptions={"name": "Full name of the user"},
        ...     frozen=True
        ... )
        >>> print(NewUser.model_fields.keys())
        dict_keys(['name', 'age', 'email'])

        >>> class AdvancedUser(BaseModel):
        ...     details: dict[str, Any]
        ...
        ...     class Config:
        ...         extra = 'allow'
        >>> EnhancedUser = new_model(
        ...     AdvancedUser,
        ...     use_all_fields=True,
        ...     inherit_base=True,
        ...     config_dict={'json_schema_extra': {'examples': [{'details': {'key': 'value'}}]}}
        ... )
        >>> print(EnhancedUser.model_config)
        {'extra': 'allow', 'json_schema_extra': {'examples': [{'details': {'key': 'value'}}]}}
    """
    if not isinstance(base, type) or not issubclass(base, BaseModel):
        if not isinstance(base, BaseModel):
            raise ValueError("base must be a Pydantic model class or instance")
        base = type(base)

    # Prepare fields
    fields = {}
    if use_all_fields and hasattr(base, "all_fields"):
        fields.update(base.all_fields)
    else:
        fields.update(base.model_fields)

    # Exclude fields
    if exclude_fields:
        for field in exclude_fields:
            fields.pop(field, None)

    # Add extra fields
    if extra_fields:
        fields.update(extra_fields)

    # Update field descriptions
    if field_descriptions:
        for field_name, description in field_descriptions.items():
            if field_name in fields:
                field_info = fields[field_name]
                if isinstance(field_info, tuple):
                    fields[field_name] = (
                        field_info[0],
                        Field(..., description=description),
                    )
                elif isinstance(field_info, FieldInfo):
                    fields[field_name] = field_info.model_copy(
                        update={"description": description}
                    )

    # Prepare config
    config = ConfigDict()
    if config_dict:
        config.update(config_dict)
    if frozen:
        config["frozen"] = True

    # Prepare class attributes
    class_kwargs = {}
    if use_base_kwargs:
        class_kwargs.update(
            {
                k: getattr(base, k)
                for k in base.__dict__
                if not k.startswith("__")
            }
        )

    # Create the model
    new_model_name = model_name or f"Dynamic{base.__name__}"
    model: type[BaseModel] = create_model(
        new_model_name, __base__=base if inherit_base else BaseModel, **fields
    )

    # Set config
    if config:
        model.model_config = config

    # Set docstring
    if doc:
        model.__doc__ = doc

    # Add validators
    if validators:
        for field, validator_func in validators.items():
            setattr(
                model,
                f"validate_{field}",
                field_validator(field)(validator_func),
            )

    # Add class attributes
    for key, value in class_kwargs.items():
        setattr(model, key, value)

    return model
