from lionabc.exceptions import LionValueError
from lionfuncs import LN_UNDEFINED
from pydantic import Field

from lion_core.form.base import BaseForm
from lion_core.form.form import Form
from lion_core.form.utils import ERR_MAP
from lion_core.generic.pile import Pile


class Report(BaseForm):
    """
    Report class that extends BaseForm to manage and track task completion.

    This class provides functionalities to create forms, track completed tasks,
    and generate reports based on a template. It is designed to manage
    multiple forms and their assignments, keeping track of completed tasks
    and their results.

    Attributes:
        default_form_template (Type[Form]): Default template for creating forms
        strict_form (bool): If True, form cannot be modified after init.
        completed_tasks (Pile[Form]): A pile of completed tasks.
        completed_task_assignments (dict[str, str]): Assignments completed for
            the report, mapping form IDs to assignments.
    """

    default_form_template: type[Form] = Form
    strict_form: bool = Field(
        default=False,
        description="If True, form cannot be modified after init.",
    )

    completed_tasks: Pile[Form] = Field(
        default_factory=lambda: Pile(item_type={Form}),
        description="A pile of tasks completed",
    )

    completed_task_assignments: dict[str, str] = Field(
        default_factory=dict,
        description="assignments completed for the report",
    )

    @property
    def work_fields(self) -> list[str]:
        """
        Get a list of work fields in the report.

        Work fields are fields that are not part of the base report structure
        but are added dynamically. These fields represent the core tasks
        or assignments being tracked in the report.

        Returns:
            list[str]: A list of work fields.
        """
        base_report_fields = self.__class__.model_fields.keys()
        all_fields = self.all_fields.keys()
        return [i for i in all_fields if i not in base_report_fields]

    def get_incomplete_fields(
        self,
        none_as_valid_value: bool = False,
    ) -> list[str]:
        """
        Get a list of incomplete fields in the report.

        This method checks all fields in the report and returns a list of those
        that are incomplete, based on whether `None` is considered a valid
        value.

        Args:
            none_as_valid_value (bool): If True, `None` is considered valid.

        Returns:
            list[str]: A list of incomplete fields.
        """
        base_report_fields = self.__class__.model_fields.keys()

        result = []
        for i in self.all_fields:
            if i in base_report_fields:
                continue
            if none_as_valid_value:
                if getattr(self, i) is LN_UNDEFINED:
                    result.append(i)
            else:
                if getattr(self, i) in [None, LN_UNDEFINED]:
                    result.append(i)
        return result

    def parse_assignment(
        self,
        input_fields: list[str],
        request_fields: list[str],
    ) -> str:
        """
        Parse and create an assignment string from input and request fields.

        This method generates an assignment string in the format
        "input_field1, input_field2 -> request_field1, request_field2".

        Args:
            input_fields (list[str]): A list of input fields.
            request_fields (list[str]): A list of request fields.

        Returns:
            str: The parsed assignment string.

        Raises:
            ValueError: If input_fields or request_fields are not lists or
                        if any field is missing from the form.
        """
        if not isinstance(input_fields, list):
            raise ERR_MAP["type", "not_list"](
                input_fields,
                "The input_fields must be a list of strings.",
            )

        if not isinstance(request_fields, list):
            raise ERR_MAP["type", "not_list"](
                request_fields,
                "The request_fields must be a list of strings.",
            )

        for i in input_fields + request_fields:
            if i not in self.all_fields:
                raise ERR_MAP["field", "missing"](i)

        input_assignment = ", ".join(input_fields)
        output_assignment = ", ".join(request_fields)
        return f"{input_assignment} -> {output_assignment}"

    def create_form(
        self,
        assignment: str,
        *,
        input_fields: list[str] | None = None,
        request_fields: list[str] | None = None,
        task_description: str | None = None,
        fill_inputs: bool | None = True,
        none_as_valid_value: bool | None = False,
        strict=None,
    ) -> Form:
        """
        Create a form based on the assignment or input/request fields.

        This method generates a new form either based on a direct assignment
        string or by parsing input and request fields to create the assignment.
        The form can be configured to pre-fill input fields and handle `None`
        values as valid or invalid.

        Args:
            assignment (str): The assignment string defining the task.
            input_fields (list[str], optional): A list of input fields.
            request_fields (list[str], optional): A list of request fields.
            task_description (str, optional): A description of the task.
            fill_inputs (bool, optional): Whether to pre-fill input fields.
            none_as_valid_value (bool, optional): Treat `None` as valid value.
            strict (bool, optional): Whether the form should be strict.

        Returns:
            Form: The created form.

        Raises:
            ValueError: If both assignment and input/request fields are
                        provided or if neither is provided.
        """
        if assignment is not None:
            if input_fields is not None or request_fields is not None:
                raise ValueError(
                    "Cannot provide input/request fields with assignment.",
                )
        else:
            if input_fields is None or request_fields is None:
                raise ValueError(
                    "Provide input_fields and request_fields lists together."
                )

        if not assignment:
            assignment = self.parse_assignment(
                input_fields=input_fields,
                request_fields=request_fields,
            )

        f_ = self.default_form_template.from_form(
            assignment=assignment,
            form=self,
            task_description=task_description,
            fill_inputs=fill_inputs,
            none_as_valid_value=none_as_valid_value,
            strict=strict if isinstance(strict, bool) else self.strict_form,
        )
        return f_

    def save_completed_form(
        self,
        form: Form,
        update_results=False,
    ) -> None:
        """
        Save a completed form to the report.

        This method adds a form to the `completed_tasks` pile, ensuring that
        all fields in the form are compatible with the report. Optionally, it
        can update the report fields with results from the form.

        Args:
            form (Form): The form to be saved.
            update_results (bool): Update the report with form results.

        Raises:
            ValueError: If the form is incomplete or if its fields do not
                        match the report's fields.
        """
        try:
            form.check_is_completed(handle_how="raise")
        except Exception as e:
            raise ValueError(f"Failed to add completed form. Error: {e}")

        report_fields = self.all_fields.keys()
        for i in form.work_dict.keys():
            if i not in report_fields:
                raise LionValueError(
                    f"The task does not match the report. "
                    f"Field {i} in task assignment not found in report."
                )

        self.completed_tasks.include(form)
        self.completed_task_assignments[form.ln_id] = form.assignment

        if update_results:
            for i in form.request_fields:
                field_result = getattr(form, i)
                setattr(self, i, field_result)

    @classmethod
    def from_form_template(
        cls,
        template_class: type[BaseForm],
        **input_kwargs,
    ) -> "Report":
        """
        Create a report from a form template.

        This method generates a report object using the fields from a specified
        form template. The report is populated with input values provided via
        keyword arguments.

        Args:
            template_class (Type[BaseForm]): The form template class to use.
            **input_kwargs: Values to initialize the report's fields.

        Returns:
            Report: The generated report.

        Raises:
            ValueError: If template class is not a subclass of `BaseForm`.
        """
        if not issubclass(template_class, BaseForm):
            raise LionValueError(
                "Invalid form template. Must be a subclass of Form.",
            )
        template_class = template_class or cls.default_form_template
        rep_template = "report_for_"
        rep_template += template_class.model_fields["template_name"].default

        report_obj = cls(template_name=rep_template)

        base_report_fields = cls.model_fields.keys()

        for field, field_info in template_class.model_fields.items():
            if field in base_report_fields:
                continue
            if field not in report_obj.all_fields:
                report_obj.add_field(field, field_obj=field_info)
            if field in input_kwargs:
                value = input_kwargs.get(field)
                setattr(report_obj, field, value)

        return report_obj

    @classmethod
    def from_form(
        cls,
        form: BaseForm,
        fill_inputs: bool = True,
    ) -> "Report":
        """
        Create a report from an existing form.

        This method generates a report object using the fields from an existing
        form, optionally filling the report with the form's input values.

        Args:
            form (BaseForm): The form to use as a template.
            fill_inputs (bool): Fill the report with form's input values.

        Returns:
            Report: The generated report.

        Raises:
            ValueError: If form is not an instance of `BaseForm`.
        """
        if not isinstance(form, BaseForm):
            raise ERR_MAP["type", "not_form_instance"](form)

        report_template_name = "report_for_" + form.template_name
        report_obj = cls(template_name=report_template_name)

        base_report_fields = cls.model_fields.keys()

        for field, field_info in form.all_fields.items():
            if field in base_report_fields:
                continue
            if field not in report_obj.all_fields:
                report_obj.add_field(field, field_obj=field_info)
            if fill_inputs:
                value = getattr(form, field)
                setattr(report_obj, field, value)

        return report_obj


__all__ = ["Report"]

# File: lion_core/form/report.py
