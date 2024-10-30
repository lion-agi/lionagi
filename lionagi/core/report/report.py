from typing import Any, Type

from lionagi.core.collections import Pile, pile
from lionagi.core.collections.abc import Field
from lionagi.core.report.base import BaseForm
from lionagi.core.report.form import Form
from lionagi.core.report.util import get_input_output_fields


class Report(BaseForm):
    """
    Extends BaseForm to handle a collection of Form instances based on specific
    assignments, managing a pile of forms and ensuring synchronization and
    proper configuration.
    """

    forms: Pile[Form] = Field(
        None,
        description="A pile of forms related to the report.",
    )

    form_assignments: list = Field(
        [],
        description="assignment for the report",
        examples=[["a, b -> c", "a -> e", "b -> f", "c -> g", "e, f, g -> h"]],
    )

    form_template: type[Form] = Field(
        Form, description="The template for the forms in the report."
    )

    def __init__(self, **kwargs):
        """
        Initializes the Report with input and requested fields based on the
        report's assignment, creating forms dynamically from provided assignments.
        """
        super().__init__(**kwargs)
        self.input_fields, self.requested_fields = get_input_output_fields(
            self.assignment
        )

        # if assignments is not provided, set it to report assignment
        if self.form_assignments == []:
            self.form_assignments.append(self.assignment)

        # create forms
        self.forms = pile(
            [self.form_template(assignment=i) for i in self.form_assignments],
            [Form, BaseForm, Report],
        )

        # Add undeclared fields to report with None values
        for v in self.forms:
            for _field in list(v.work_fields.keys()):
                if _field not in self._all_fields:
                    field_obj = v._all_fields[_field]
                    self._add_field(_field, value=None, field_obj=field_obj)

        # Synchronize fields between report and forms
        for k, v in self._all_fields.items():
            if getattr(self, k, None) is not None:
                for _form in self.forms:
                    if k in _form.work_fields:
                        _form.fill(**{k: getattr(self, k)})

    @property
    def work_fields(self) -> dict[str, Any]:
        all_fields = {}
        for form in self.forms.values():
            for k, v in form.work_fields.items():
                if k not in all_fields:
                    all_fields[k] = v
        return all_fields

    def fill(
        self,
        form: Form | list[Form] | dict[Form] = None,
        strict=True,
        **kwargs,
    ):
        if self.filled:
            if strict:
                raise ValueError("Form is filled, cannot be worked on again")

        # gather all unique valid fields from input form,
        # kwargs and self workfields data
        all_fields = self._get_all_fields(form, **kwargs)

        # if there are information in the forms that are not in the report,
        # add them to the report
        for k, v in all_fields.items():
            if k in self.work_fields and getattr(self, k, None) is None:
                setattr(self, k, v)

        # if there are information in the report that are not in the forms,
        # add them to the forms
        for _form in self.forms:
            for k, v in _form.work_fields.items():
                _kwargs = {}
                if v is None and (a := getattr(self, k, None)) is not None:
                    _kwargs[k] = a
                _form.fill(**_kwargs)

    def is_workable(self) -> bool:
        """
        Checks if the report is ready for processing, ensuring all necessary fields
        are filled and output fields are unique across forms.

        Returns:
            bool: True if the report is workable, otherwise raises ValueError.
        """
        if self.filled:
            raise ValueError(
                "Form is already filled, cannot be worked on again"
            )

        for i in self.input_fields:
            if not getattr(self, i, None):
                raise ValueError(f"Required field {i} is not provided")

        # this is the required fields from report's own assignment
        fields = self.input_fields
        fields.extend(self.requested_fields)

        # if the report's own assignment is not in the forms, return False
        for f in fields:
            if f not in self.work_fields:
                raise ValueError(f"Field {f} is not in the forms")

        # get all the output fields from all the forms
        outs = []
        for form in self.forms.values():
            outs.extend(form.requested_fields)

        # all output fields should be unique, not a single output field should be
        # calculated by more than one form
        if len(outs) != len(set(outs)):
            raise ValueError("Output fields are not unique")

        return True

    def next_forms(self) -> Pile[Form]:
        """
        Returns a pile of workable forms based on current form states within the report.

        Returns:
            Pile[Form]: A pile of workable forms or None if there are no workable forms.
        """
        a = [i for i in self.forms if i.workable]
        return pile(a, Form) if len(a) > 0 else None
