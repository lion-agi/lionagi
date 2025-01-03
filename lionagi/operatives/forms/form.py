# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from typing import Any, Literal, TypeVar

from pydantic import Field, model_validator
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from typing_extensions import override

from lionagi.utils import UNDEFINED, copy

from ..models.note import Note
from .base import BaseForm
from .utils import get_input_output_fields

T = TypeVar("T", bound=BaseForm)


class Form(BaseForm):
    """
    Base task form class extending BaseForm with task-specific functionality.

    This class builds on BaseForm to introduce concepts specific to task-based
    forms, including input fields, request fields, and task-related attributes
    It is designed for tasks that require filling in fields through an
    intelligent process, providing the necessary framework for managing and
    validating these fields.

    Key Concepts:
    - input_fields: Fields required to obtain the request fields.
    - request_fields: Fields that need to be filled by an intelligent process.
    - output_fields: Fields for presentation, which may include all, some, or
      none of the request fields. These can be conditionally modified if the
      form is not strict_form.

    The Form class provides methods for field management, validation, and
    task instruction generation. It supports both strict_form and flexible
    modes of operation, allowing for immutable fields and assignments when
    needed.

    Attributes:
        strict_form (bool): If True, form fields and assignment are immutable.
        guidance (str | dict[str, Any] | None): High-level task guidance that
            can be optimized by AI or provided as instructions.
        input_fields (list[str]): Fields needed to obtain the requested fields.
        request_fields (list[str]): Fields to be filled by an intelligent
            process.
        task (Any): The work to be done, including custom instructions.
        task_description (str | None): A detailed description of the task.
        init_input_kwargs (dict[str, Any]): Initial keyword arguments for
            input fields.

    Example:
        >>> form = Form(
        ...     assignment="input1, input2 -> output",
        ...     strict_form=True,
        ...     guidance="Complete the task with the given inputs."
        ... )
        >>> form.fill_input_fields(input1="value1", input2="value2")
        >>> print(form.get_results())
    """

    strict_form: bool = Field(
        default=False,
        description="If True, form fields and assignment are immutable.",
        frozen=True,
    )
    guidance: str | dict[str, Any] | None = Field(
        default=None,
        description="High-level task guidance, optimizable by AI.",
    )
    input_fields: list[str] = Field(
        default_factory=list,
        description="Fields required to obtain the requested fields.",
    )
    request_fields: list[str] = Field(
        default_factory=list,
        description="Fields to be filled by an intelligent process.",
    )
    task: Any = Field(
        default_factory=str,
        description="Work to be done, including custom instructions.",
    )
    task_description: str | None = Field(
        default_factory=str,
        description="Detailed description of the task",
    )
    init_input_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        exclude=True,
    )

    def check_is_completed(
        self,
        handle_how: Literal["return_missing", "raise"] = "raise",
    ) -> list[str] | None:
        """Check if all required fields are completed.

        Args:
            handle_how: How to handle incomplete fields.

        Returns:
            List of incomplete fields if handle_how is "return_missing",
            None otherwise.

        Raises:
            ValueError: If required fields are incomplete and handle_how
                is "raise".
        """
        if self.strict_form and self.has_processed:
            return
        return super().check_is_completed(handle_how)

    @model_validator(mode="before")
    @classmethod
    def check_input_output_list_omitted(cls, data: Any) -> dict[str, Any]:
        """Validate and process the input data before model creation.

        Args:
            data: The input data for model creation.

        Returns:
            The validated and processed input data.

        Raises:
            ValueError: If the input data is invalid or missing required fields
        """
        if isinstance(data, Note):
            data = data.to_dict()

        if not isinstance(data, dict):
            raise TypeError("Input data must be a dictionary.")

        if not data.get("assignment", None):
            if cls.model_fields["assignment"].get_default() is None:
                raise ValueError("Assignment is missing.")
            else:
                data["assignment"] = cls.model_fields[
                    "assignment"
                ].get_default()

        if "input_fields" in data:
            raise ValueError("Explicit input fields are not allowed.")

        if "request_fields" in data:
            raise ValueError("Explicit request fields are not allowed.")

        if "task" in data:
            raise ValueError("Explicit task fields are not allowed.")

        fields = get_input_output_fields(data.get("assignment"))
        input_fields, request_fields = fields

        if not input_fields or input_fields == [""]:
            raise ValueError("Missing input fields.")

        elif not request_fields or request_fields == [""]:
            raise ValueError("Missing request fields.")

        data["input_fields"] = input_fields
        data["request_fields"] = request_fields
        data["output_fields"] = data.get("output_fields", request_fields)
        data["init_input_kwargs"] = {}
        data["strict_form"] = data.get("strict_form", False)

        for in_ in data["input_fields"]:
            data["init_input_kwargs"][in_] = (
                data.pop(in_, UNDEFINED)
                if in_ not in cls.model_fields
                else data.get(in_, UNDEFINED)
            )

        return data

    @model_validator(mode="after")
    def check_input_output_fields(self) -> "Form":
        """
        Validate and process input and output fields after model creation.

        Returns:
            The validated Form instance.
        """
        for i in self.input_fields:
            if i in self.model_fields:
                self.init_input_kwargs[i] = getattr(self, i)
            else:
                self.add_field(
                    i,
                    value=self.init_input_kwargs.get(i, UNDEFINED),
                )

        for i in self.request_fields:
            if i not in self.all_fields:
                self.add_field(i)

        return self

    @override
    @property
    def work_fields(self) -> list[str]:
        """Return a list of all fields involved in the task."""
        return self.input_fields + self.request_fields

    @override
    @property
    def required_fields(self) -> list[str]:
        """Return a list of all unique required fields."""
        return list(
            set(self.input_fields + self.request_fields + self.output_fields),
        )

    @property
    def validation_kwargs(self):
        """Get validation keyword arguments for each work field."""
        dict_ = {}
        for i in self.work_fields:
            dict_[i] = self.field_getattr(i, "validation_kwargs", {})
        return dict_

    @property
    def instruction_dict(self) -> dict[str, Any]:
        """Return a dictionary with task instruction information."""
        return {
            "context": self.instruction_context,
            "instruction": self.instruction_prompt,
            "request_fields": self.instruction_request_fields,
        }

    @property
    def instruction_context(self) -> str:
        """Generate a description of the form's input fields."""
        a = self.all_fields
        context = "### Input Fields:\n"
        for idx, i in enumerate(self.input_fields):
            context += f"Input No.{idx+1}: {i}\n"
            if getattr(a[i], "description", None):
                context += f"  - description: {a[i].description}.\n"
            context += f"  - value: {getattr(self, i)}.\n"
        return context

    @property
    def instruction_prompt(self) -> str:
        """Generate a task instruction prompt for the form."""
        a = self.all_fields
        prompt = ""
        if "guidance" in a:
            prompt += f"### Overall Guidance:\n{getattr(self, 'guidance')}.\n"

        in_fields = ", ".join(self.input_fields)
        out_fields = ", ".join(self.output_fields)
        prompt += "### Task Instructions:\n"
        prompt += f"1. Provided Input Fields: {in_fields}.\n"
        prompt += f"2. Requested Output Fields: {out_fields}.\n"
        prompt += f"3. Your task:\n{self.task}.\n"

        return prompt

    @property
    def instruction_request_fields(self) -> dict[str, str]:
        """Get descriptions of the form's requested fields."""
        a = self.all_fields

        context = "### Output Fields:\n"
        for idx, i in enumerate(self.request_fields):
            context += f"Input No.{idx+1}: {i}\n"
            if getattr(a[i], "description", None):
                context += f"  - description: {a[i].description}.\n"
            if getattr(a[i], "examples", None):
                context += f"  - examples: {a[i].examples}.\n"

        return context

    @override
    def update_field(
        self,
        field_name: str,
        value: Any = UNDEFINED,
        annotation: Any = UNDEFINED,
        field_obj: FieldInfo | Any = UNDEFINED,
        **kwargs: Any,
    ) -> None:
        """Update a field in the form.

        Extends the base update_field method to also update the
        init_input_kwargs dictionary.

        Args:
            field_name: The name of the field to update.
            value: The value to assign to the field.
            annotation: The type annotation for the field.
            field_obj: The field object containing metadata.
            **kwargs: Additional keyword arguments for field configuration.
        """
        super().update_field(
            field_name,
            value=value,
            annotation=annotation,
            field_obj=field_obj,
            **kwargs,
        )
        self._fill_init_input_kwargs(field_name)

    @override
    def __setattr__(self, field_name: str, value: Any) -> None:
        """Set an attribute of the form.

        This method enforces the strict_form attribute, preventing
        modifications to certain fields when strict_form mode is enabled.

        Args:
            field_name: The name of the attribute to set.
            value: The value to assign to the attribute.

        Raises:
            ValueError: If attempting to modify a restrict_formed field
                        in strict_form mode.
        """
        if self.strict_form and field_name in {
            "assignment",
            "input_fields",
            "request_fields",
        }:
            raise ValueError(
                f"Cannot modify {field_name} in strict form mode."
            )

        if field_name in {"input_fields", "request_fields"}:
            raise ValueError("Cannot modify input or request fields.")

        if field_name in {"init_input_kwargs"}:
            raise ValueError(f"Cannot modify restricted field {field_name}.")

        super().__setattr__(field_name, value)
        self._fill_init_input_kwargs(field_name)

    def _fill_init_input_kwargs(self, field_name: str) -> None:
        """Update init_input_kwargs if the field is an input field."""
        if field_name in self.input_fields:
            self.init_input_kwargs[field_name] = getattr(self, field_name)

    def check_is_workable(
        self,
        handle_how: Literal["raise", "return_missing"] = "raise",
    ) -> list[str] | None:
        """Check if all input fields are filled and the form is workable.

        Args:
            handle_how: How to handle missing inputs.

        Returns:
            List of missing inputs if handle_how is "return_missing",
            None otherwise.

        Raises:
            ValueError: If input fields are missing and handle_how is
                        "raise".
        """
        if self.strict_form and self.has_processed:
            raise ValueError("Cannot modify processed form in strict mode.")

        missing_inputs = []
        invalid_values = [UNDEFINED, PydanticUndefined]
        if not self.none_as_valid_value:
            invalid_values.append(None)

        for i in self.input_fields:
            if getattr(self, i) in invalid_values:
                missing_inputs.append(i)

        if missing_inputs:
            if handle_how == "raise":
                raise ValueError(f"Incomplete input fields: {missing_inputs}")
            elif handle_how == "return_missing":
                return missing_inputs

    def is_completed(self) -> bool:
        """Check if the form has been completed."""
        try:
            self.check_is_completed(handle_how="raise")
            return True
        except Exception:
            return False

    def is_workable(self) -> bool:
        """Check if the form is workable."""
        try:
            self.check_is_workable(handle_how="raise")
            return True
        except Exception:
            return False

    def to_dict(self, *, valid_only: bool = False) -> dict[str, Any]:
        """Convert the form to a dictionary.

        Args:
            valid_only: Whether to include only valid fields in the output.

        Returns:
            A dictionary representation of the form.
        """
        _dict = super().to_dict()
        if not valid_only:
            return _dict

        disallow_values = [UNDEFINED, PydanticUndefined]
        if not self.none_as_valid_value:
            disallow_values.append(None)
        return {k: v for k, v in _dict.items() if v not in disallow_values}

    @override
    @classmethod
    def from_dict(cls, data: dict, **kwargs) -> T:
        """Create a Form instance from a dictionary.

        Args:
            data: The input data for creating the form.
            **kwargs: Additional keyword arguments.

        Returns:
            The created Form instance.
        """
        input_data = copy(data)

        input_data.pop("lion_class", None)
        input_data.pop("input_fields", None)
        input_data.pop("request_fields", None)
        task = input_data.pop("task", "")

        extra_fields = {}
        for k, v in list(input_data.items()):
            if k not in cls.model_fields:
                extra_fields[k] = input_data.pop(k)
        obj = cls.model_validate(input_data, **kwargs)
        obj.task = task
        for k, v in extra_fields.items():
            obj.update_field(field_name=k, value=v)

        metadata = copy(data.get("metadata", {}))
        last_updated = metadata.get("last_updated", None)
        if last_updated is not None:
            obj.metadata.set(["last_updated"], last_updated)
        else:
            obj.metadata.pop(["last_updated"], None)
        return obj

    def fill_input_fields(
        self,
        form: BaseForm | Any = None,
        **value_kwargs,
    ) -> None:
        """Fill the form's input fields with values.

        Args:
            form: A form to copy values from.
            **value_kwargs: Values to use for filling the input fields.

        Raises:
            TypeError: If the provided form is not a BaseForm instance.
        """
        if form is not None and not isinstance(form, BaseForm):
            raise TypeError("Provided form is not a BaseForm instance.")

        for i in self.input_fields:
            if self.none_as_valid_value:
                if getattr(self, i) is not UNDEFINED:
                    continue
                value = value_kwargs.get(i, UNDEFINED)
                if value is UNDEFINED:
                    value = copy(getattr(form, i, UNDEFINED))
                if value is not UNDEFINED:
                    setattr(self, i, value)
            else:
                if getattr(self, i) in [UNDEFINED, None]:
                    value = value_kwargs.get(i)
                    if value in [UNDEFINED, None]:
                        value = copy(getattr(form, i, UNDEFINED))
                    if value not in [UNDEFINED, None]:
                        setattr(self, i, value)

    def fill_request_fields(
        self,
        form: BaseForm = None,
        **value_kwargs,
    ) -> None:
        """Fill the form's request fields with values.

        Args:
            form: A form to copy values from.
            **value_kwargs: Values to use for filling the request fields.

        Raises:
            TypeError: If the provided form is not a BaseForm instance.
        """
        if form is not None and not isinstance(form, BaseForm):
            raise TypeError("Provided form is not a BaseForm instance.")

        for i in self.request_fields:
            if self.none_as_valid_value:
                if getattr(self, i) is not UNDEFINED:
                    continue
                value = value_kwargs.get(i, UNDEFINED)
                if value is UNDEFINED:
                    value = copy(getattr(form, i, UNDEFINED))
                if value is not UNDEFINED:
                    setattr(self, i, value)
            else:
                if getattr(self, i) in [UNDEFINED, None]:
                    value = value_kwargs.get(i)
                    if value in [UNDEFINED, None]:
                        value = copy(getattr(form, i, UNDEFINED))
                    if value not in [UNDEFINED, None]:
                        setattr(self, i, value)

    @classmethod
    def from_form(
        cls,
        form: BaseForm | type[BaseForm],
        guidance: str | dict[str, Any] | None = None,
        assignment: str | None = None,
        strict_form: bool = False,
        task_description: str | None = None,
        fill_inputs: bool = True,
        none_as_valid_value: bool = False,
        output_fields: list[str] | None = None,
        same_form_output_fields: bool = False,
        **input_value_kwargs,
    ) -> "Form":
        """Create a Form instance from another form.

        Args:
            form: The form to copy from.
            guidance: Guidance for the new form.
            assignment: The assignment for the new form.
            strict_form: Whether the new form should be strict_form.
            task_description: A description of the task.
            fill_inputs: Whether to fill input fields.
            none_as_valid_value: Whether to treat None as a valid value.
            output_fields: Output fields for the new form.
            same_form_output_fields: Whether to copy output fields from the
                original form.
            **input_value_kwargs: Values for filling the new form's input
                                fields.

        Returns:
            The created Form instance.

        Raises:
            TypeError: If the provided form is not a BaseForm or its subclass.
            ValueError: If both output_fields and same_form_output_fields are
                        provided.
        """
        if inspect.isclass(form):
            if not issubclass(form, BaseForm):
                raise TypeError("Provided form is not a BaseForm class.")
            form_fields = form.model_fields
        else:
            if not isinstance(form, BaseForm):
                raise TypeError("Provided form is not a BaseForm instance.")
            form_fields = form.all_fields

        if same_form_output_fields:
            if output_fields:
                raise ValueError(
                    "Cannot provide output_fields and "
                    "same_form_output_fields at the same time."
                )
            output_fields = copy(form.output_fields)

        if not assignment:
            if not getattr(form, "assignment", None):
                raise ValueError("Assignment is missing.")
            assignment = form.assignment

        obj = cls(
            guidance=guidance or getattr(form, "guidance", None),
            assignment=assignment,
            task_description=task_description
            or getattr(
                form,
                "task_description",
                "",
            ),
            none_as_valid_value=none_as_valid_value
            or getattr(form, "none_as_valid_value", False),
            strict_form=strict_form or getattr(form, "strict_form", False),
            output_fields=output_fields,
        )

        for i in obj.work_fields:
            if i not in form_fields:
                raise ValueError(f"Invalid assignment field: {i}")
            obj.update_field(i, field_obj=form_fields[i])

        if fill_inputs:
            if inspect.isclass(form):
                obj.fill_input_fields(**input_value_kwargs)
            else:
                obj.fill_input_fields(form=form, **input_value_kwargs)

        return obj

    def remove_request_from_output(self) -> None:
        """Remove the request fields from the output fields."""
        for i in self.request_fields:
            if i in self.output_fields:
                self.output_fields.remove(i)

    def _append_to_one(
        self,
        field_name: str,
        field_type: Literal["input", "output", "request"],
        value: Any = UNDEFINED,
        annotation: Any = UNDEFINED,
        field_obj: FieldInfo | Any = UNDEFINED,
        **kwargs,
    ) -> None:
        """Append a field to one of the field lists.

        Args:
            field_name: The name of the field to append.
            field_type: The type of field to append.
            value: The value of the field.
            annotation: The type annotation for the field.
            field_obj: The field object containing metadata.
            **kwargs: Additional keyword arguments for field configuration.

        Raises:
            ValueError: If the field type is invalid or if appending to
                input or request fields in strict_form mode.
        """

        if self.strict_form and field_type in {"input", "request"}:
            raise ValueError(
                f"Cannot modify {field_type} fields in strict form mode."
            )

        config = {
            "field_name": field_name,
            "value": value,
            "annotation": annotation,
            "field_obj": field_obj,
            **kwargs,
        }

        match field_type:
            case "input":
                if field_name not in self.input_fields:
                    self.input_fields.append(field_name)
                if field_name not in self.assignment:
                    self.assignment = f"{field_name}, " + self.assignment

            case "request":
                if field_name not in self.request_fields:
                    self.request_fields.append(field_name)
                    config.pop("value")
                if field_name not in self.assignment:
                    self.assignment += f", {field_name}"

            case "output":
                if field_name not in self.output_fields:
                    self.output_fields.append(field_name)

            case _:
                raise ValueError(f"Invalid field type {field_type}")

        if (
            any(
                [
                    value is not UNDEFINED,
                    annotation is not UNDEFINED,
                    field_obj is not UNDEFINED,
                    bool(kwargs),
                ]
            )
            or field_name not in self.all_fields
        ):
            self.update_field(**config)

    def append_to_input(
        self,
        field_name: str,
        value: Any = UNDEFINED,
        annotation: Any = UNDEFINED,
        field_obj: FieldInfo | Any = UNDEFINED,
        **kwargs,
    ) -> None:
        """Append a field to the input fields.

        Args:
            field_name: The name of the field to append.
            value: The value of the field.
            annotation: The type annotation for the field.
            field_obj: The field object containing metadata.
            **kwargs: Additional keyword arguments for field configuration.

        Raises:
            ValueError: If appending the field fails.
        """
        try:
            self._append_to_one(
                field_name=field_name,
                field_type="input",
                value=value,
                annotation=annotation,
                field_obj=field_obj,
                **kwargs,
            )
        except Exception as e:
            raise ValueError(
                f"Failed to append {field_name} to input fields."
            ) from e

    def append_to_output(
        self,
        field_name: str,
        value: Any = UNDEFINED,
        annotation: Any = UNDEFINED,
        field_obj: FieldInfo | Any = UNDEFINED,
        **kwargs,
    ) -> None:
        """Append a field to the output fields.

        Args:
            field_name: The name of the field to append.
            value: The value of the field.
            annotation: The type annotation for the field.
            field_obj: The field object containing metadata.
            **kwargs: Additional keyword arguments for field configuration.

        Raises:
            ValueError: If appending the field fails.
        """

        try:
            self._append_to_one(
                field_name=field_name,
                field_type="output",
                value=value,
                annotation=annotation,
                field_obj=field_obj,
                **kwargs,
            )
        except Exception as e:
            raise ValueError(
                f"Failed to append {field_name} to output fields."
            ) from e

    def append_to_request(
        self,
        field_name: str,
        annotation: Any = UNDEFINED,
        field_obj: FieldInfo | Any = UNDEFINED,
        **kwargs,
    ) -> None:
        """Append a field to the request fields.

        Args:
            field_name: The name of the field to append.
            value: The value of the field.
            annotation: The type annotation for the field.
            field_obj: The field object containing metadata.
            **kwargs: Additional keyword arguments for field configuration.

        Raises:
            ValueError: If appending the field fails.
        """
        if "value" in kwargs:
            raise ValueError("Cannot provide value to request fields.")
        try:
            self._append_to_one(
                field_name=field_name,
                field_type="request",
                annotation=annotation,
                field_obj=field_obj,
                **kwargs,
            )
        except Exception as e:
            raise ValueError(
                f"Failed to append {field_name} to request fields."
            ) from e


__all__ = ["Form"]
