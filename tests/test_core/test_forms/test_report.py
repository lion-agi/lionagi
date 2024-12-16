import pytest
from pydantic import Field

from lionagi.core.forms.form import Form
from lionagi.core.forms.report import Report
from lionagi.core.generic.types import Pile
from lionagi.core.typing import UNDEFINED


class SimpleReport(Report):
    """A simple report class for testing."""

    field1: str = Field(default="value1")
    field2: int | None = Field(default=None)
    field3: str = Field(default=UNDEFINED)


class SimpleForm(Form):
    """A simple form class for testing."""

    input1: str = Field(default=UNDEFINED)
    output1: str = Field(default=UNDEFINED)
    shared_field: str = Field(default=UNDEFINED)


def test_report_initialization():
    """Test basic initialization of Report."""
    report = Report(template_name="test_report")
    assert report.template_name == "test_report"
    assert not report.strict_form
    assert isinstance(report.completed_tasks, Pile)
    assert isinstance(report.completed_task_assignments, dict)


def test_parse_assignment():
    """Test parse_assignment method."""
    report = SimpleReport()

    # Test valid parsing
    assignment = report.parse_assignment(
        input_fields=["field1"],
        request_fields=["field2"],
    )
    assert assignment == "field1 -> field2"

    # Test with invalid fields
    with pytest.raises(ValueError):
        report.parse_assignment(
            input_fields=["nonexistent"],
            request_fields=["field1"],
        )

    # Test with invalid input types
    with pytest.raises(TypeError):
        report.parse_assignment(
            input_fields="not_a_list",
            request_fields=["field1"],
        )


def test_create_form():
    """Test create_form method."""
    report = SimpleReport()

    # Test creating form with assignment string
    form = report.create_form(
        assignment="field1 -> field2",
        task_description="Test task",
    )
    assert form.assignment == "field1 -> field2"
    assert form.task_description == "Test task"

    # Test creating form with input/request fields
    form = report.create_form(
        assignment=None,
        input_fields=["field1"],
        request_fields=["field2"],
    )
    assert form.input_fields == ["field1"]
    assert form.request_fields == ["field2"]

    # Test invalid creation
    with pytest.raises(ValueError):
        report.create_form(
            assignment="field1 -> field2",
            input_fields=["field1"],  # Can't provide both
        )


def test_save_completed_form():
    """Test save_completed_form method."""
    report = SimpleReport()
    form = report.create_form(
        assignment="field1 -> field2",
        none_as_valid_value=False,
    )

    # Test saving incomplete form
    with pytest.raises(ValueError, match="Incomplete request fields"):
        report.save_completed_form(form)

    # Complete and save form
    form.field2 = 42
    report.save_completed_form(form)
    assert form in report.completed_tasks
    assert form.ln_id in report.completed_task_assignments

    # Test updating results
    report.field2 = None  # Reset field
    report.save_completed_form(form, update_results=True)
    assert report.field2 == 42  # Should be updated from form


def test_from_form_template():
    """Test from_form_template class method."""
    # Test creating report from form template
    report = Report.from_form_template(SimpleForm)
    assert hasattr(report, "input1")
    assert hasattr(report, "output1")
    assert hasattr(report, "shared_field")

    # Test with input values
    report = Report.from_form_template(
        SimpleForm,
        input1="custom_input",
    )
    assert report.input1 == "custom_input"

    # Test with invalid template
    with pytest.raises(ValueError):
        Report.from_form_template(str)  # Not a BaseForm subclass


def test_from_form():
    """Test from_form class method."""
    # Create a form with assignment to make it valid
    form = SimpleForm(assignment="input1 -> output1")
    form.input1 = "test_input"
    form.shared_field = "test_shared"

    # Test creating report from form instance
    report = Report.from_form(form, fill_inputs=True)
    assert report.input1 == "test_input"
    assert report.shared_field == "test_shared"

    # Test with fill_inputs=False
    report = Report.from_form(form, fill_inputs=False)
    assert report.input1 is UNDEFINED

    # Test with invalid form
    with pytest.raises(TypeError):
        Report.from_form("not a form")


def test_template_name_generation():
    """Test template name generation."""
    # Test default template name
    form = SimpleForm(assignment="input1 -> output1")
    report = Report.from_form(form)
    assert report.template_name.startswith("report_for_")

    # Test custom template name
    form = SimpleForm(
        assignment="input1 -> output1",
        template_name="custom_template",
    )
    report = Report.from_form(form)
    assert report.template_name == "report_for_custom_template"


def test_completed_tasks_management():
    """Test completed tasks management."""
    report = SimpleReport()
    form1 = report.create_form(
        assignment="field1 -> field2",
        none_as_valid_value=False,
    )
    form2 = report.create_form(
        assignment="field1 -> field3",
        none_as_valid_value=False,
    )

    # Complete and save forms
    form1.field2 = 42
    form2.field3 = "test"

    report.save_completed_form(form1)
    report.save_completed_form(form2)

    # Check completed tasks tracking
    assert len(report.completed_tasks) == 2
    assert len(report.completed_task_assignments) == 2
    assert form1.assignment in report.completed_task_assignments.values()
    assert form2.assignment in report.completed_task_assignments.values()
