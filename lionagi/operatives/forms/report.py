# forms/report.py

from pydantic import Field

from lionagi.protocols.generic.pile import Pile

from .base import BaseForm
from .form import Form


class Report(BaseForm):
    """
    A minimal class that collects multiple completed forms as sub-tasks.
    For instance, if you have multiple forms representing each step or sub-process,
    you can store them all here.
    """

    default_form_cls: type[Form] = Form
    completed_forms: Pile[Form] = Field(
        default_factory=lambda: Pile(item_type={Form}),
        description="A collection of completed forms.",
    )
    form_assignments: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping from form ID -> assignment string",
    )

    def add_completed_form(
        self, form: Form, update_report_fields: bool = False
    ):
        """
        Add a completed form.
        If update_report_fields=True, we copy the form's output fields back into this report object.
        """
        missing = form.check_completeness()
        if missing:
            raise ValueError(
                f"Form {form.id} is incomplete: missing {missing}."
            )
        self.completed_forms.append(form)
        self.form_assignments[form.id] = form.assignment or ""

        if update_report_fields:
            for f_ in form.output_fields:
                val = getattr(form, f_, None)
                setattr(self, f_, val)
