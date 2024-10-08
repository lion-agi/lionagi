from typing import Any, Literal

from lionabc import MutableRecord
from lionabc.exceptions import LionValueError
from lionfuncs import LN_UNDEFINED
from pydantic import Field, field_validator
from pydantic_core import PydanticUndefined

from lion_core.form.utils import ERR_MAP
from lion_core.generic.component import Component


class BaseForm(Component, MutableRecord):
    """Base form class providing core functionality for form handling.

    This class serves as a foundation for creating custom forms within the
    lion-core library. It includes methods for managing output fields,
    handling results, and applying field annotations.

    The BaseForm class focuses on output fields, which are fields that are
    presented as the result of form processing. Output fields can include all,
    part, or none of the request fields and can be conditionally modified by
    the process if the form is not set to be strict.

    Attributes:
        assignment: The objective of the task, which may define how input
            fields are processed into output fields.
        template_name: The name of the form template.
        output_fields: A list of field names that are outputted and presented
            by the form.
        none_as_valid_value: Indicates whether to treat None as a valid value
            when processing output fields.
        has_processed: Indicates if the task has been processed.

    Example:
        >>> form = BaseForm(
        ...     assignment="input1, input2 -> output",
        ...     output_fields=["output1", "output2"],
        ... )
        >>> result = form.get_results()
        >>> print(result)
    """

    assignment: str | None = Field(
        default=None,
        description="The objective of the task.",
        examples=["input1, input2 -> output"],
    )
    template_name: str = Field(
        default="default_form", description="Name of the form template"
    )
    output_fields: list[str] = Field(
        default_factory=list,
        description="Fields that are outputted and presented by the form.",
    )
    none_as_valid_value: bool = Field(
        default=False,
        description="Indicate whether to treat None as a valid value.",
    )
    has_processed: bool = Field(
        default=False,
        description="Indicates if the task has been processed.",
        exclude=True,
    )

    def check_is_completed(
        self,
        handle_how: Literal["raise", "return_missing"] = "raise",
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
        non_complete_request = []
        invalid_values = [LN_UNDEFINED, PydanticUndefined]
        if not self.none_as_valid_value:
            invalid_values.append(None)

        for i in self.required_fields:
            if getattr(self, i) in invalid_values:
                non_complete_request.append(i)

        if non_complete_request:
            if handle_how == "raise":
                raise ERR_MAP["assignment", "incomplete_request"](
                    non_complete_request,
                )
            elif handle_how == "return_missing":
                return non_complete_request
        else:
            self.has_processed = True

    def is_completed(self) -> bool:
        """Check if the form is completed.

        Returns:
            True if the form is completed, False otherwise.
        """
        try:
            self.check_is_completed(handle_how="raise")
            return True
        except Exception:
            return False

    @field_validator("output_fields", mode="before")
    @classmethod
    def _validate_output(cls, value):
        """Validate the output_fields attribute.

        Args:
            value: The value to validate.

        Returns:
            The validated value.

        Raises:
            LionValueError: If the value is invalid.
        """
        if isinstance(value, str):
            return [value]
        if isinstance(value, list) and all(
            [i for i in value if isinstance(i, str)],
        ):
            return value
        if not value:
            return []
        raise LionValueError("Invalid output fields.")

    @property
    def work_fields(self) -> list[str]:
        """Get the list of fields that are outputted by the form.

        Returns:
            A list of field names.
        """
        return self.output_fields

    @property
    def work_dict(self) -> dict[str, Any]:
        """Get a dictionary of all work fields and their values.

        Returns:
            A dictionary of field names and their values.
        """
        return {i: getattr(self, i, LN_UNDEFINED) for i in self.work_fields}

    @property
    def required_fields(self) -> list[str]:
        """Get the list of required fields for the form.

        Returns:
            A list of required field names.
        """
        return self.output_fields

    @property
    def required_dict(self) -> dict[str, Any]:
        """Get a dictionary of all required fields and their values.

        Returns:
            A dictionary of required field names and their values.
        """
        dict_ = {}
        for i in self.required_fields:
            dict_[i] = getattr(self, i, LN_UNDEFINED)

        return dict_

    def get_results(
        self,
        suppress: bool = False,
        valid_only: bool = False,
    ) -> dict[str, Any]:
        """Retrieve the results of the form.

        Args:
            suppress: If True, suppress errors for missing fields.
            valid_only: If True, return only valid (non-empty) results.

        Returns:
            A dictionary of field names and their values.

        Raises:
            ValueError: If a required field is missing and suppress is False.
        """
        result = {}
        out_fields = self.output_fields or getattr(self, "request_fields", [])

        for i in out_fields:
            if i not in self.all_fields:
                if not suppress:
                    raise ERR_MAP["field", "missing"](i)
            else:
                result[i] = getattr(self, i, LN_UNDEFINED)

        # add a validator for output fields

        if valid_only:
            invalid_values = [
                LN_UNDEFINED,
                PydanticUndefined,
            ]
            if not self.none_as_valid_value:
                invalid_values.append(None)

            res_ = {}
            for k, v in result.items():
                if v not in invalid_values:
                    res_[k] = v
            result = res_

        return result

    @property
    def display_dict(self) -> dict[str, Any]:
        """
        Get a dictionary of the required fields and their values for display.

        Returns:
            A dictionary of required field names and their values.
        """
        return self.required_dict


__all__ = ["BaseForm"]
