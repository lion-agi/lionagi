"""Tests for the report module."""

import pytest
from pydantic import Field

from lionagi.operatives.forms.form import Form
from lionagi.operatives.forms.report import Report
from lionagi.protocols.generic.pile import Pile
from lionagi.utils import UNDEFINED


class SimpleForm(Form):
    """A simple form class for testing."""

    input1: str = Field(default=UNDEFINED)
    output1: str = Field(default=UNDEFINED)
    shared_field: str = Field(default=UNDEFINED)


def test_report_initialization():
    """Test basic initialization of Report."""
    report = Report()
    assert isinstance(report.completed_forms, Pile)
    assert isinstance(report.form_assignments, dict)
    assert report.default_form_cls == Form


def test_add_completed_form():
    """Test add_completed_form method."""
    report = Report()
    form = Form(assignment="input -> output")

    # Try to add incomplete form
    with pytest.raises(ValueError, match="Form .* is incomplete"):
        report.add_completed_form(form)

    # Complete and add form
    form.output = "test output"
    report.add_completed_form(form)
    assert len(report.completed_forms) == 1
    assert form.id in report.form_assignments
    assert report.form_assignments[form.id] == "input -> output"


def test_add_completed_form_with_update():
    """Test add_completed_form with field updates."""
    report = Report()
    form = Form(assignment="input -> output")
    form.output = "test value"

    # Add form and update report fields
    report.add_completed_form(form, update_report_fields=True)
    assert getattr(report, "output") == "test value"


def test_multiple_forms():
    """Test handling multiple forms."""
    report = Report()

    # Create and complete first form
    form1 = Form(assignment="a -> b")
    form1.b = "value1"
    report.add_completed_form(form1)

    # Create and complete second form
    form2 = Form(assignment="x -> y")
    form2.y = "value2"
    report.add_completed_form(form2)

    # Verify both forms are tracked
    assert len(report.completed_forms) == 2
    assert len(report.form_assignments) == 2
    assert form1.id in report.form_assignments
    assert form2.id in report.form_assignments


def test_report_with_flow():
    """Test report with multi-step forms."""
    report = Report()

    # Create and complete a multi-step form
    form = Form(assignment="a->b; b->c")
    form.b = "intermediate"
    form.c = "final"

    report.add_completed_form(form, update_report_fields=True)
    assert getattr(report, "c") == "final"
    assert form.id in report.form_assignments


def test_report_field_updates():
    """Test field update behavior."""
    report = Report()

    # Add first form without updates
    form1 = Form(assignment="x -> y")
    form1.y = "value1"
    report.add_completed_form(form1)
    assert not hasattr(report, "y")

    # Add second form with updates
    form2 = Form(assignment="a -> b")
    form2.b = "value2"
    report.add_completed_form(form2, update_report_fields=True)
    assert getattr(report, "b") == "value2"
