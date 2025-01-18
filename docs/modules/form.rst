======================================
Form & Flow
======================================

The forms module provides a flexible system for handling structured data transformations
through forms and multi-step flows. It consists of four core components:

1. :class:`BaseForm` - Foundation for form handling
2. :class:`Form` - Enhanced form with input/output field distinction
3. :class:`FlowDefinition` - Multi-step transformation pipeline
4. :class:`Report` - Aggregator for completed forms

-----------
Base Form
-----------

.. module:: lionagi.operatives.forms.base
   :synopsis: Core form functionality.

.. class:: BaseForm

   **Inherits from**: :class:`lionagi.protocols.generic.element.Element`

   A minimal form class that tracks output fields and validates completeness.
   Uses Pydantic v2 with ``ConfigDict(extra="allow", arbitrary_types_allowed=True)``.

   **Attributes**:

   - **assignment** (*str | None*) -- A DSL string describing the transformation
   - **output_fields** (*list[str]*) -- Fields considered mandatory outputs
   - **none_as_valid** (*bool*) -- If True, None is accepted as valid
   - **has_processed** (*bool*) -- Marks if form is completed

   **Methods**:

   .. method:: is_completed() -> bool

      Check if all required output fields are set and valid.
      A field is considered valid if:
      
      - It exists and has a value
      - The value is not UNDEFINED
      - If none_as_valid=False, the value is not None

   .. method:: check_completeness(how: Literal["raise", "return_missing"]) -> list[str]

      Return missing required fields or raise an exception.

      Parameters:
         - **how** -- If "raise", raises ValueError for missing fields.
           If "return_missing", returns list of missing field names.

   .. method:: get_results(valid_only: bool = False) -> dict[str, Any]

      Return a dict of output fields, optionally filtering invalid values.

      Parameters:
         - **valid_only** -- If True, omit fields with None/UNDEFINED values
           (depending on none_as_valid setting)

   **Example**::

      from lionagi.operatives.forms import BaseForm

      form = BaseForm(
          output_fields=["result"],
          none_as_valid=False
      )
      form.result = "computation complete"
      assert form.is_completed()
      print(form.get_results())  # {"result": "computation complete"}

      # With none_as_valid=True
      form = BaseForm(
          output_fields=["optional_result"],
          none_as_valid=True
      )
      form.optional_result = None
      assert form.is_completed()  # True, None is valid

-----------
Flow System
-----------

.. module:: lionagi.operatives.forms.flow
   :synopsis: Multi-step flow handling.

.. class:: FlowStep

   **Inherits from**: :class:`pydantic.BaseModel`

   A single transformation step in a multi-step flow.
   Uses Pydantic v2 with ``ConfigDict(arbitrary_types_allowed=True)``.

   **Attributes**:

   - **name** (*str*) -- Step identifier (e.g., "step_1")
   - **inputs** (*list[str]*) -- Required input fields for this step
   - **outputs** (*list[str]*) -- Fields produced by this step
   - **description** (*str | None*) -- Optional step documentation

.. class:: FlowDefinition

   **Inherits from**: :class:`pydantic.BaseModel`

   Manages a sequence of transformation steps using a DSL.
   Uses Pydantic v2 with ``ConfigDict(arbitrary_types_allowed=True)``.

   **Attributes**:

   - **steps** (*List[FlowStep]*) -- Ordered list of transformation steps

   **Methods**:

   .. method:: parse_flow_string(flow_str: str)

      Parse a DSL string like "a,b->c; c->d" into FlowSteps.
      Each step is named sequentially (step_1, step_2, etc.).
      Empty segments and whitespace are handled gracefully.

   .. method:: get_required_fields() -> set[str]

      Return fields needed as inputs but not produced by prior steps.
      For example, in "a->b; b,c->d", returns {"a", "c"} since:
      
      - "a" is needed by step 1 but not produced earlier
      - "b" is needed by step 2 but produced by step 1
      - "c" is needed by step 2 but not produced earlier

   .. method:: get_produced_fields() -> set[str]

      Return all fields produced by any step.
      For example, in "a->b,c; c->d", returns {"b", "c", "d"}.

   **Example**::

      from lionagi.operatives.forms import FlowDefinition

      flow = FlowDefinition()
      
      # Parse text processing pipeline
      flow.parse_flow_string(
          "text->tokens; tokens->embeddings; embeddings->clusters"
      )
      
      print(flow.get_required_fields())  # {"text"}
      print(flow.get_produced_fields())  # {"tokens", "embeddings", "clusters"}
      
      # Steps are named sequentially
      for step in flow.steps:
          print(f"{step.name}: {step.inputs} -> {step.outputs}")

------
Form
------

.. module:: lionagi.operatives.forms.form
   :synopsis: Enhanced form with input/output distinction.

.. class:: Form

   **Inherits from**: :class:`BaseForm`

   A form that distinguishes between input and request (output) fields.
   Uses Pydantic v2 with ``ConfigDict(extra="allow", arbitrary_types_allowed=True)``.

   **Attributes**:

   - **flow_definition** (*Optional[FlowDefinition]*) -- For multi-step flows
   - **guidance** (*str | None*) -- Optional processing guidance
   - **task** (*str | None*) -- Task description

   **Validators**:

   - **parse_assignment_into_flow**: Creates FlowDefinition for multi-step assignments
   - **compute_output_fields**: Sets output_fields based on assignment or flow

   **Methods**:

   .. method:: fill_fields(**kwargs)

      Update form fields with provided values.
      Useful for partial updates when you don't want to recreate the form.

   .. method:: to_instructions() -> dict[str, Any]

      Return a dictionary suitable for LLM consumption, containing:
      
      - assignment: The DSL string
      - flow: FlowDefinition as dict (if multi-step)
      - guidance: Optional processing guidance
      - task: Optional task description
      - required_outputs: List of required output fields

   **Example**::

      from lionagi.operatives.forms import Form

      # Single-step form
      form = Form(assignment="user_input->greeting")
      form.fill_fields(user_input="Alice")
      
      # Multi-step form with all produced fields as outputs
      form = Form(
          assignment="name,age->profile; profile->recommendation",
          guidance="Generate personalized recommendations",
          task="User profiling"
      )
      
      # The flow is automatically parsed
      assert form.flow_definition is not None
      assert len(form.flow_definition.steps) == 2
      
      # All produced fields are outputs
      assert set(form.output_fields) == {"profile", "recommendation"}

--------
Report
--------

.. module:: lionagi.operatives.forms.report
   :synopsis: Form aggregation and tracking.

.. class:: Report

   **Inherits from**: :class:`BaseForm`

   Collects and manages multiple completed forms.
   Uses Pydantic v2 with ``ConfigDict(extra="allow", arbitrary_types_allowed=True)``.

   **Attributes**:

   - **default_form_cls** (*type[Form]*) -- Form class to use (defaults to Form)
   - **completed_forms** (*Pile[Form]*) -- Thread-safe collection of completed forms
   - **form_assignments** (*dict[str, str]*) -- Maps form IDs to assignments

   **Methods**:

   .. method:: add_completed_form(form: Form, update_report_fields: bool = False)

      Add a completed form to the report.

      Parameters:
         - **form** -- A completed Form instance
         - **update_report_fields** -- If True, copy form's output values to report

      Raises:
         - ValueError if form is incomplete

   **Example**::

      from lionagi.operatives.forms import Report, Form

      report = Report()
      
      # Create and complete forms for a multi-step process
      form1 = Form(assignment="query->embeddings")
      form1.fill_fields(
          query="What's the weather?",
          embeddings=[0.1, 0.2, 0.3]
      )
      
      form2 = Form(assignment="embeddings->answer")
      form2.fill_fields(
          embeddings=form1.embeddings,
          answer="Sunny with a high of 75°F"
      )
      
      # Add both forms, updating report fields from the final form
      report.add_completed_form(form1)
      report.add_completed_form(form2, update_report_fields=True)
      
      print(report.answer)  # "Sunny with a high of 75°F"

--------------------
Additional Notes
--------------------

**DSL Format**

The forms system uses a simple DSL (Domain Specific Language) for describing
transformations:

- Single step: ``input1, input2 -> output``
- Multiple steps: ``a,b->c; c->d``
- Spaces are allowed: ``input1, input2  ->  output``

The DSL is parsed into either:

1. Simple input/output field lists for :class:`Form`
2. A full :class:`FlowDefinition` for multi-step processes

**Multi-step Flow Behavior**

When using multi-step flows:

1. Each step's outputs become available to later steps as inputs
2. The form's output_fields include all produced fields by default
3. You can override output_fields to select specific outputs
4. Required fields are those needed as inputs but not produced by prior steps

**Best Practices**

1. Use :class:`BaseForm` when you only need output validation
2. Use :class:`Form` when distinguishing inputs from outputs
3. Use :class:`FlowDefinition` for complex multi-step transformations
4. Use :class:`Report` to track multiple related forms
5. Set none_as_valid=True when fields may legitimately be None
6. Provide guidance and task descriptions for better LLM interaction

**Type Safety**

All form classes use Pydantic v2 for validation. You can create typed forms by
subclassing and adding type hints::

   from pydantic import Field
   from lionagi.utils import UNDEFINED

   class UserForm(Form):
       name: str = Field(default=UNDEFINED)
       age: int = Field(default=UNDEFINED)
       profile: str | None = Field(default=None)
       
       model_config = ConfigDict(
           extra="allow",
           arbitrary_types_allowed=True
       )

This ensures type safety and proper validation for form fields.
