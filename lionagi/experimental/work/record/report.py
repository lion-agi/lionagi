from typing import Any, Type
from pydantic import Field

from .._status import WorkStatus
from ._util import get_input_output_fields
from .form import Form, Record


class Report(Record):
    """
    Represents a detailed report composed of multiple forms, which are dynamically created
    based on specified assignments. This class manages the aggregation of form data and
    evaluates the completion and workability of the report based on the filled status
    and correctness of its forms.

    Attributes:
        forms (Dict[str, Form]): Forms associated with this report, keyed by assignment.
        form_assignments (List[str]): Assignments specifically designated for this report.
        form_template (Type[Form]): The class used as a template to instantiate new forms.
    """

    forms: dict[str, Form] = Field(
        default_factory=dict,
        description="A dictionary of forms related to the report, in {assignment: Form} format.",
    )

    form_assignments: list = Field(
        [],
        description="assignment for the report",
        examples=[["a, b -> c", "a -> e", "b -> f", "c -> g", "e, f, g -> h"]],
    )

    form_template: Type[Form] = Field(
        Form, 
        description="The template for the forms in the report."
    )

    def __init__(self, **kwargs):
        """
        Initializes the report by setting up forms based on assignments.
        Fields are set to None unless explicitly provided.
        """
        super().__init__(**kwargs)
        self.input_fields, self.output_fields = get_input_output_fields(self.assignment)

        # if assignments is not provided, set it to assignment
        if self.form_assignments == []:
            self.form_assignments.append(self.assignment)
        
        self._initialize()


    def _initialize(self):
        """
        Initializes forms based on the specified assignments using the form template.
        Sets any undefined fields to None and merges existing data if present. Ensures 
        all fields required by the form are initialized in the report, setting them to 
        None if not already defined.
        """
        new_forms = {i: self.form_template(assignment=i) for i in self.form_assignments}

        for k, v in new_forms.items():
            if k not in self.forms:
                self.forms[k] = v

        for k, v in self.forms.items():
            for f in list(v.work_fields.keys()):
                if f not in self._all_fields:
                    if  v._all_fields.get(f, None) is None:
                        v._add_field(f, value=None)
                    field = v._all_fields[f]
                    self._add_field(f, value=None, field=field)

        for k, v in self._all_fields.items():
            if getattr(self, k, None) is not None:
                for f in self.forms.values():
                    if k in f.work_fields:
                        f.fill(**{k: getattr(self, k)})

    @property
    def work_fields(self) -> dict[str, Any]:
        """
        Aggregates all work-related fields across all forms.

        Returns:
            A dictionary of all fields used for work across forms.
        """
        all_fields = {}
        for form in self.forms.values():
            all_fields.update(**{k:v for k, v in form.work_fields.items() if k not in all_fields})
        return all_fields

    def fill(self, **kwargs):
        """
        Fills the report and its associated forms with provided data, updating
        the report's status based on its workability and completeness.
        """
        kwargs = {**self.work_fields, **kwargs}
        for k, v in kwargs.items():
            if k in self.work_fields and getattr(self, k, None) is None:
                setattr(self, k, v)

        for form in self.forms.values():
            if not form.filled:
                form.fill(**{k: v for k, v in kwargs.items() if k in form.work_fields})

        self.update_status()

    def update_status(self):
        """
        Updates the status of the report based on its completion and workability.
        """
        if self.filled:
            self.status = WorkStatus.COMPLETED
        elif self.workable:
            self.status = WorkStatus.IN_PROGRESS
        else:
            self.status = WorkStatus.PENDING

    @property
    def filled(self) -> bool:
        """
        Determines if all required fields across the forms are filled.

        Returns:
            True if all fields are filled, False otherwise.
        """

        return all(value is not None for value in self.work_fields.values())

    @property
    def workable(self) -> bool:
        """
        Checks if the report is workable based on the readiness of its forms.

        Returns:
            True if the report can be processed, False otherwise.
        """
        try:
            self.check_workable()
            return True
        except ValueError:
            return False

    def check_workable(self) -> bool:
        """
        Validates that all necessary input fields are filled and checks for unique output fields.

        Raises:
            ValueError: If any required fields are missing or if duplicate output fields are found.

        Returns:
            True if the report is ready for processing, otherwise False.
        """
        if self.filled:
            raise ValueError("The report is already filled and cannot be worked on again.")

        if missing_fields := [
            f for f in self.input_fields if getattr(self, f, None) is None]:
            raise ValueError(f"Fields {missing_fields} are required to work on the report.")
        
        # get all the output fields from all the forms
        output_fields = []
        for form in self.forms.values():
            output_fields.extend(form.output_fields)

        # all output fields should be unique, not a single output field should be
        # calculated by more than one form
        if len(output_fields) != len(set(output_fields)):
            raise ValueError("Duplicate output fields detected in the forms.")

        return True

    @property
    def next_forms(self) -> list[Form] | None:
        """
        Filters and returns forms that are currently workable.

        Returns:
            A list of workable forms, or None if no forms are workable.
        """
        workable_forms = [form for form in self.forms.values() if form.workable]
        return workable_forms if workable_forms else None

