import json
from typing import Any, Dict

from lionagi.core.collections.abc import SYSTEM_FIELDS
from lionagi.core.report.base import BaseForm
from lionagi.core.report.util import get_input_output_fields


class Form(BaseForm):
    """
    A specialized implementation of BaseForm designed to manage form fields
    dynamically based on specified assignments. Supports initialization and
    management of input and requested fields, handles form filling operations,
    and ensures forms are properly configured for use.

    Attributes:
        input_fields (List[str]): Fields required to carry out the objective of the form.
        requested_fields (List[str]): Fields requested to be filled by the user.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new instance of the Form, setting up input and requested
        fields based on the form's assignment.
        """
        super().__init__(**kwargs)
        self.input_fields, self.requested_fields = get_input_output_fields(
            self.assignment
        )

        for i in self.input_fields:
            self.append_to_input(i)

        for i in self.input_fields + self.requested_fields:
            if i not in self._all_fields:
                self._add_field(i, value=None)

    def append_to_request(self, field: str, value=None):
        """
        Appends a field to the requested fields.

        Args:
            field (str): The name of the field to be requested.
            value (optional): The value to be assigned to the field. Defaults to None.
        """
        if "," in field:
            field = field.split(",")
        if not isinstance(field, list):
            field = [field]

        for i in field:
            i = i.strip()
            if i not in self._all_fields:
                self._add_field(i, value=value)

            if i not in self.requested_fields:
                self.requested_fields.append(i)
                self.validation_kwargs[i] = self._get_field_attr(
                    i, "validation_kwargs", {}
                )

    def append_to_input(self, field: str, value=None):
        """
        Appends a field to the input fields.

        Args:
            field (str): The name of the field to be added to input.
            value (optional): The value to be assigned to the field. Defaults to None.
        """
        if "," in field:
            field = field.split(",")
        if not isinstance(field, list):
            field = [field]

        for i in field:
            i = i.strip()
            if i not in self._all_fields:
                self._add_field(i, value=value)

            if i not in self.input_fields:
                self.input_fields.append(i)
                self.validation_kwargs[i] = self._get_field_attr(
                    i, "validation_kwargs", {}
                )

    @property
    def work_fields(self) -> dict[str, Any]:
        """
        Retrieves a dictionary of the fields relevant to the current task,
        excluding any SYSTEM_FIELDS and including only the input and requested
        fields.

        Returns:
            Dict[str, Any]: The relevant fields for the current task.
        """
        dict_ = self.to_dict()
        return {
            k: v
            for k, v in dict_.items()
            if k not in SYSTEM_FIELDS
            and k in self.input_fields + self.requested_fields
        }

    def fill(self, form: "Form" = None, strict: bool = True, **kwargs) -> None:
        """
        Fills the form from another form instance or provided keyword arguments.
        Raises an error if the form is already filled.

        Args:
            form (Form, optional): The form to fill from.
            strict (bool, optional): Whether to enforce strict filling. Defaults to True.
            **kwargs: Additional fields to fill.
        """
        if self.filled:
            if strict:
                raise ValueError("Form is filled, cannot be worked on again")

        all_fields = self._get_all_fields(form, **kwargs)

        for k, v in all_fields.items():
            if (
                k in self.work_fields
                and v is not None
                and getattr(self, k, None) is None
            ):
                setattr(self, k, v)

    def is_workable(self) -> bool:
        """
        Determines if the form is ready for processing. Checks if all required
        fields are filled and raises an error if the form is already filled or
        if any required field is missing.

        Returns:
            bool: True if the form is workable, otherwise raises ValueError.
        """
        if self.filled:
            raise ValueError(
                "Form is already filled, cannot be worked on again"
            )

        for i in self.input_fields:
            if not getattr(self, i, None):
                raise ValueError(f"Required field {i} is not provided")

        return True

    @property
    def _instruction_context(self) -> str:
        """
        Generates a detailed description of the input fields, including their
        current values and descriptions.

        Returns:
            str: A detailed description of the input fields.
        """
        return "".join(
            f"""
        ## input: {i}:
        - description: {getattr(self._all_fields[i], "description", "N/A")}
        - value: {str(getattr(self, self.input_fields[idx]))}
        """
            for idx, i in enumerate(self.input_fields)
        )

    @property
    def _instruction_prompt(self) -> str:
        return f"""
        ## Task Instructions
        Please follow prompts to complete the task:
        1. Your task is: {self.task}
        2. The provided input fields are: {', '.join(self.input_fields)}
        3. The requested output fields are: {', '.join(self.requested_fields)}
        4. Provide your response in the specified JSON format.
        """

    @property
    def _instruction_requested_fields(self) -> dict[str, str]:
        """
        Provides a dictionary mapping requested field names to their
        descriptions.

        Returns:
            Dict[str, str]: A dictionary of requested field descriptions.
        """
        return {
            i: getattr(self._all_fields[i], "description", "N/A")
            for i in self.requested_fields
        }

    def display(self, fields=None):
        """
        Displays the form fields using IPython display.

        Args:
            fields (optional): Specific fields to display. Defaults to None.
        """
        from IPython.display import Markdown, display

        fields = fields or self.work_fields

        if "answer" in fields:
            answer = fields.pop("answer")
            fields["answer"] = answer

        for k, v in fields.items():
            if isinstance(v, dict):
                v = json.dumps(v, indent=4)
            if len(str(v)) > 50:
                display(Markdown(f"**{k}**: \n {v}"))
            else:
                display(Markdown(f"**{k}**: {v}"))
