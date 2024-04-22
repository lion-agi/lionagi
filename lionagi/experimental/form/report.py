from typing import Any
from pydantic import Field
from lionagi.experimental.form.form import Form
from lionagi import logging as _logging


class Report(Form):

    assignment: str = Field(
        ..., 
        examples=["a, b -> h"]
    )

    forms: dict[str, Form] = Field(
        default_factory=dict,
        description="A dictionary of forms related to the report, in {form.id_: form} format."
    )

    assignments: list = Field(
        [],
        description="assignment for the report", 
        examples=[["a, b -> c", "a -> e", "b -> f", "c -> g", "e, f, g -> h"]]
    )

    def fill(self, form: Form | str = None, **kwargs):
        if form:
            form: Form = self.forms[form] if isinstance(form, str) else form
            if not form.filled or form not in self.forms.values():
                raise ValueError("The form is not filled or not in the report.")
            
            for k, v in form.work_fields.items():
                if k not in self.model_fields:
                    field = form.model_fields[k]
                    self._add_field(k, value=v, field=field)
        else:
            for k, v in kwargs.items():
                if k in self.model_fields:
                    self._add_field(k, v)

    @property
    def filled(self) -> bool:
        return all([value is not None for _, value in self.work_fields.items()])
    
    @property
    def work_fields(self) -> dict[str, Any]:
        """
        all work fields across all forms, including intermediate output fields
        """
        all_fields = {}
        for form in self.forms.values():
            for k, v in form.work_fields.items():
                if k not in all_fields:
                    all_fields[k] = v
        return all_fields

    @property
    def _filled_forms(self) -> list[Form]:
        return [form for form in self.forms.values() if form.filled]

    @property
    def _unfilled_forms(self) -> list[Form]:
        return [form for form in self.forms.values() if not form.filled]

    @property
    def _filled_fields(self) -> list[str]:
        filled_fields = []
        for i in self.work_fields:
            if getattr(self, i, None) is not None:
                filled_fields.append(i)
        return filled_fields

    @property
    def _unfilled_fields(self) -> list[str]:
        return [i for i in self.work_fields if i not in self._filled_fields]

    @property
    def workable(self) -> bool:

        fields = self.input_fields
        fields.extend(self.output_fields)

        for f in fields:
            if f not in self.work_fields:
                _logging.error(f"Field {f} is not assigned in the forms for the report.")
                return False

        outs = []
        for form in self.forms.values():
            outs.extend(form.output_fields)

        if len(outs) != len(set(outs)):
            _logging.error(f"Output fields should be unique across all forms.")
            return False

        return True

    @property
    def next_forms(self) -> list[Form] | None:
        to_do = []
        for i in self._unfilled_forms:
            if all([j in self._filled_fields for j in i.input_fields]):
                to_do.append(i)
        return to_do if len(to_do) > 0 else None
