from ..generic.abc.util import SYSTEM_FIELDS
from .util import get_input_output_fields
from .base import BaseForm


class Form(BaseForm):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_fields, self.requested_fields = get_input_output_fields(
            self.assignment
        )
        for i in self.input_fields + self.requested_fields:
            if i not in self._all_fields:
                self._add_field(i, value=None)

    @property
    def work_fields(self):
        dict_ = self.to_dict()
        return {
            k: v
            for k, v in dict_.items()
            if k not in SYSTEM_FIELDS and k in self.input_fields + self.requested_fields
        }

    def fill(self, form: "Form" = None, **kwargs):
        if self.filled:
            raise ValueError("Form is already filled")

        all_fields = self._get_all_fields(form, **kwargs)

        for k, v in all_fields.items():
            if (
                k in self.work_fields
                and v is not None
                and getattr(self, k, None) is None
            ):
                setattr(self, k, v)

    def is_workable(self):
        if self.filled:
            raise ValueError("Form is already filled, cannot be worked on again")

        for i in self.input_fields:
            if not getattr(self, i, None):
                raise ValueError(f"Required field {i} is not provided")

        return True

    @property
    def _instruction_context(self):
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
    def _instruction_prompt(self):
        ccc = f"""
        0. Your in is {self.task},
        1. provided: {self.input_fields}, 
        2. requested: {self.requested_fields}
        ----------
        """
        return ccc.replace("        ", "")

    @property
    def _instruction_requested_fields(self):
        return {i: getattr(self._all_fields[i], "description", "N/A") for i in self.requested_fields}