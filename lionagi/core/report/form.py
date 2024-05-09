import contextlib
from ..generic.abc import Component, Field
from .util import get_input_output_fields, system_fields


class Form(Component):

    assignment: str = Field(..., examples=["input1, input2 -> output"])
    input_fields: list[str] = Field(default_factory=list)
    requested_fields: list[str] = Field(default_factory=list)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.input_fields, self.requested_fields = get_input_output_fields(
            self.assignment
        )
        for i in self.input_fields + self.requested_fields:
            if i not in self.model_fields:
                self._add_field(i, value=None)

    @property
    def filled(self):
        with contextlib.suppress(ValueError):
            return self._is_filled()
        return False

    @property
    def workable(self):
        with contextlib.suppress(ValueError):
            return self._is_workable()
        return False

    @property
    def work_fields(self):
        dict_ = self.to_dict()
        return {
            k: v
            for k, v in dict_.items()
            if k not in system_fields and k in self.input_fields + self.requested_fields
        }

    def fill(self, form: "Form" = None, **kwargs):
        """
        only work fields for this form can be filled
        a field can only be filled once
        """
        if self.filled:
            raise ValueError("Form is already filled")

        fields = form.work_fields if form else {}
        kwargs = {**fields, **kwargs}

        for k, v in kwargs.items():
            if k not in self.work_fields:
                raise ValueError(f"Field {k} is not a valid work field")
            setattr(self, k, v)

    def _is_workable(self):
        if self.filled:
            raise ValueError("Form is already filled, cannot be worked on again")

        for i in self.input_fields:
            if not getattr(self, i, None):
                raise ValueError(f"Required field {i} is not provided")

        return True

    def _is_filled(self):
        for k, value in self.work_fields.items():
            if value is None:
                raise ValueError(f"Field {k} is not filled")
        return True
