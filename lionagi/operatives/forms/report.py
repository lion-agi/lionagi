# forms/report.py

from pydantic import Field

from lionagi.protocols.generic.pile import Pile

from .base import BaseForm
from .form import Form


class Report(BaseForm):
    """
    A minimal class that collects multiple completed forms as "sub-tasks."
    If you have a single FlowDefinition that describes the entire multi-step pipeline,
    you can track each step as a separate form in here.
    """

    default_form_cls: type[Form] = Form
    completed_forms: Pile[Form] = Field(
        default_factory=lambda: Pile(item_type={Form}),
        description="A list of forms that have been completed for this report.",
    )
    form_assignments: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping from form ID -> assignment string",
    )

    def add_completed_form(
        self, form: Form, update_report_fields: bool = False
    ):
        """
        Add a completed form. Optionally update the report’s fields from the form's output.
        """
        missing = form.check_completeness()
        if missing:
            raise ValueError(
                f"Form {form.id} is incomplete: missing {missing}."
            )
        self.completed_forms.append(form)
        self.form_assignments[form.id] = form.assignment or ""
        # optionally update the report’s own fields
        if update_report_fields:
            for f_ in form.output_fields:
                val = getattr(form, f_, None)
                setattr(self, f_, val)
