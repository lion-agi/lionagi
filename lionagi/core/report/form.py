from .util import get_input_output_fields, system_fields
from .base import BaseForm


class Form(BaseForm):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.input_fields, self.requested_fields = get_input_output_fields(
            self.assignment
        )
        for i in self.input_fields + self.requested_fields:
            if i not in self.model_fields:
                self._add_field(i, value=None)

    @property
    def work_fields(self):
        dict_ = self.to_dict()
        return {
            k: v
            for k, v in dict_.items()
            if k not in system_fields and k in self.input_fields + self.requested_fields
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
