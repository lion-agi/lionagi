"""
This module extends the BaseForm class to implement the Form class, which
dynamically manages form operations based on specific assignments. It provides
functionalities for initializing fields, filling forms with data, and
validating the readiness of forms for further processing.
"""

from ..generic.abc.util import SYSTEM_FIELDS
from .util import get_input_output_fields
from .base import BaseForm


class Form(BaseForm):
    """
    A specialized implementation of BaseForm designed to manage form fields
    dynamically based on specified assignments. Supports initialization and
    management of input and requested fields, handles form filling operations,
    and ensures forms are properly configured for use.
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
        for i in self.input_fields + self.requested_fields:
            if i not in self._all_fields:
                self._add_field(i, value=None)

    @property
    def work_fields(self) -> dict:
        """
        Retrieves a dictionary of the fields relevant to the current task,
        excluding any SYSTEM_FIELDS and including only the input and requested
        fields.
        """
        dict_ = self.to_dict()
        return {
            k: v
            for k, v in dict_.items()
            if k not in SYSTEM_FIELDS and k in self.input_fields + self.requested_fields
        }

    def fill(self, form: "Form" = None, strict=True, **kwargs):
        """
        Fills the form from another form instance or provided keyword arguments.
        Raises an error if the form is already filled. return a bool indicating
        is the filling operation was successful.
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
        """
        if self.filled:
            raise ValueError("Form is already filled, cannot be worked on again")

        for i in self.input_fields:
            if not getattr(self, i, None):
                raise ValueError(f"Required field {i} is not provided")

        return True

    @property
    def _instruction_context(self) -> str:
        """
        Generates a detailed description of the input fields, including their
        current values and descriptions.
        """
        a = "".join(
            f"""
        ## input: {i}:
        - description: {getattr(self._all_fields[i], "description", "N/A")}
        - value: {str(self.__getattribute__(self.input_fields[idx]))}
        """
            for idx, i in enumerate(self.input_fields)
        )
        return a.replace("        ", "")

    @property
    def _instruction_prompt(self) -> str:
        """
        Generates a brief summary of the form's context, including the task
        description and lists of provided and requested fields.
        """
        ccc = f"""
        0. Your in is {self.task},
        1. provided: {self.input_fields}, 
        2. requested: {self.requested_fields}
        ----------
        """
        return ccc.replace("        ", "")

    @property
    def _instruction_requested_fields(self) -> dict:
        """
        Provides a dictionary mapping requested field names to their
        descriptions.
        """
        return {
            i: getattr(self._all_fields[i], "description", "N/A")
            for i in self.requested_fields
        }
