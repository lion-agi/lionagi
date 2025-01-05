======================================
Form & Report
======================================

This module provides **form-based data structures** for tasks that involve
collecting inputs, producing outputs, and managing intermediate fields. A form
can be seen as a specialized, dynamic Pydantic model (extending LionAGI’s
:class:`OperableModel`) that captures:

- **Required** fields (input vs. request)
- **Optional** or dynamically added fields
- **Validation** (check if inputs are complete)
- **Task assignment** logic (mapping input fields to requested outputs)

Three core classes are provided:

1. :class:`BaseForm` – Foundation for form handling (output fields, checks).
2. :class:`Form` – Builds on :class:`BaseForm` for typical “input -> output”
   tasks. Automates assignment parsing and input/request field distinction.
3. :class:`Report` – Aggregates multiple completed forms, storing tasks that
   have been processed and generating a final “report.”


-----------
1. BaseForm
-----------

.. module:: lionagi.form.base
   :synopsis: Core functionality for form handling.

.. class:: BaseForm

A minimal form that tracks:

- **Assignment**: The objective or mapping from inputs to outputs.
- **Output fields**: The subset of fields to present as results.
- **has_processed**: Whether the form was fully validated/used.
- **none_as_valid_value**: If True, treating `None` as a valid field.

**Key Methods**:

- :meth:`check_is_completed(handle_how='raise'|'return_missing')`:
  Ensures required fields are populated; either raise an error or
  return the missing fields list.

- :meth:`is_completed() -> bool`:
  True if form is fully valid (no missing fields).

- :meth:`get_results(suppress=False, valid_only=False) -> dict`:
  Gather the output fields as a dictionary, optionally ignoring invalid fields.

**Example**::

   from lionagi.form.base import BaseForm

   form = BaseForm(
       assignment="some_field -> output_field",
       output_fields=["output_field"]
   )
   # Suppose we add a new field
   form.add_field("some_field", value="hello")
   # Now get results
   results = form.get_results()
   print(results)  # => {'output_field': UNDEFINED}, since not assigned


------
2. Form
------

.. module:: lionagi.form.form
   :synopsis: Extended form with distinct input and request fields.

.. class:: Form

This class distinguishes three sets of fields:

1. **input_fields** (provided by user or environment).
2. **request_fields** (which an “intelligent process” should fill).
3. **output_fields** (which are ultimately displayed or returned).

Additionally:

- **strict_form** (bool): If True, you cannot modify input/request fields or
  assignment after initialization.
- :meth:`fill_input_fields(...)` and :meth:`fill_request_fields(...)`
  let you programmatically populate these sets of fields from another form
  or via direct keyword arguments.

**Assignment**:

By default, a string in the format ``input1, input2 -> request1, request2``
defines which fields are “inputs” vs. “requests.” The class automatically
parses them if you pass an ``assignment``.

**Key Methods**:

- :meth:`check_is_workable()` / :meth:`is_workable()`:
  Verify input fields are filled so the form can proceed.

- :meth:`from_form(...)`:
  Clone or derive a new :class:`Form` from an existing :class:`BaseForm`.

- :meth:`create_form(...)`:
  (In :class:`Report`) to create a new :class:`Form` with specified
  assignment or fields.

**Example**::

   from lionagi.form.form import Form

   # assignment = "user_name, user_age -> recommended_action"
   f = Form(assignment="user_name, user_age -> recommended_action")

   # Now we add or fill the input fields
   f.fill_input_fields(user_name="Alice", user_age=30)
   # The request field is 'recommended_action'
   # We can fill it or let the AI fill it

   f.check_is_workable()     # ensures inputs exist
   # ...
   # Later we fill request
   f.fill_request_fields(recommended_action="Provide discounts")
   print(f.get_results())    # => {"recommended_action": "Provide discounts"}


--------
3. Report
--------

.. module:: lionagi.form.report
   :synopsis: Aggregates multiple completed :class:`Form` objects.

.. class:: Report

Designed to collect **multiple tasks** (forms) into one object:

- :attr:`completed_tasks`: A pile of :class:`Form` instances that are done.
- :meth:`save_completed_form(form, update_results=False)`:
  Store a completed form in the report. Optionally update the report’s
  fields with the form’s results.
- :meth:`create_form(...)`:
  Helper for building new tasks (forms) from the report’s perspective.
- :meth:`from_form(...)`:
  Alternative constructor that transforms an existing form into a report.

**Example**::

   from lionagi.form.report import Report, Form

   r = Report()
   # Suppose we create a form
   f = r.create_form(assignment="input1 -> output1")
   f.fill_input_fields(input1="Hello")

   # Mark the form as completed
   # In reality you'd fill the request field as well
   f.fill_request_fields(output1="World")
   f.check_is_completed()

   # Save into report
   r.save_completed_form(f, update_results=True)
   print(r.completed_tasks.size())       # => 1
   print(r.output1)                      # => "World" (copied from the form)


--------------------
Additional Utilities
--------------------

**Parsing**:

:func:`get_input_output_fields(str_) -> (list[str], list[str])`
Splits an assignment string of the form `input1, input2 -> request1, request2`
into two lists (input fields, request fields).

Used internally by :class:`Form` to auto-generate `input_fields` and `request_fields`.

```python
from lionagi.form.utils import get_input_output_fields

inp, req = get_input_output_fields("name, age -> greeting")
print(inp)  # ["name", "age"]
print(req)  # ["greeting"]
