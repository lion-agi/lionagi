# Form System API Reference

## Overview

The Form system manages task processing through two main components:
- Form: Handles individual task processing with field validation and value tracking
- Report: Manages collections of forms and tracks task completion states

## Form Class

Manages individual task forms with field validation and value tracking.

```python
class Form(BaseForm):
    """Task-specific form with field management."""
    
    guidance: str | dict | None     # High-level task guidance for AI
    input_fields: list[str]         # Fields required for processing
    request_fields: list[str]       # Fields to be filled by the task
    task: Any                       # Specific task instructions
    strict_form: bool = False       # Prevent field modifications if True
```

### Key Methods

```python
def fill_input_fields(self, form: BaseForm | Any = None, **value_kwargs) -> None:
    """Fill form's input fields from source or kwargs.
    
    Args:
        form: Source form to copy values from
        **value_kwargs: Direct field values

    Raises:
        ValueError: If field not found or strict_form violated
    """

def check_is_workable(self, handle_how: Literal["raise", "return_missing"]) -> list[str] | None:
    """Verify input fields are filled and form can be processed.
    
    Args:
        handle_how: How to handle missing fields
            "raise": Raise ValueError
            "return_missing": Return list of missing fields
    """

@property
def instruction_dict(self) -> dict[str, Any]:
    """Get structured task instructions with:
    - context: Input field descriptions
    - prompt: Task guidance and instructions  
    - request_fields: Required output fields
    """
```

### Usage Examples

```python
# Create and fill form
form = Form(
    assignment="text_input, max_length -> summary",  # input -> output
    guidance="Summarize text within length limit",   # AI guidance
    task="Create concise summary preserving key points"  # Specific task
)

# Fill required inputs
form.fill_input_fields(
    text_input="Long text to summarize...",
    max_length=100
)

# Verify workability
if form.check_is_workable(handle_how="return_missing"):
    print("Missing required inputs")

# Get AI instructions
instructions = form.instruction_dict  # For passing to AI
```

## Report Class

Manages form collections and tracks task completion states.

```python
class Report(BaseForm):
    """Task completion tracker and aggregator."""
    
    completed_tasks: Pile[Form]               # Storage for completed forms
    completed_task_assignments: dict[str, str]  # Maps IDs to assignments
    strict_form: bool = False                 # Lock form structure
```

### Key Methods

```python
def create_form(
    self,
    assignment: str = None,              # input -> output format
    input_fields: list[str] = None,      # or specify fields directly
    request_fields: list[str] = None,
    task_description: str = None,        # task details
    fill_inputs: bool = True             # copy report values to form
) -> Form:
    """Create form either from assignment string or field lists.
    
    The form can be created in two ways:
    1. From assignment: "input1, input2 -> output"
    2. From field lists: input_fields=["input1", "input2"], request_fields=["output"]
    """

def save_completed_form(self, form: Form, update_results: bool = False) -> None:
    """Save completed form and optionally update report fields.
    
    Args:
        form: Completed form to save
        update_results: Whether to copy form results to report
        
    Raises:
        ValueError: If form incomplete or fields mismatch
    """
    
def get_incomplete_fields(self, none_as_valid_value: bool = False) -> list[str]:
    """Get list of fields still needing values.
    
    Args:
        none_as_valid_value: Whether None is considered valid
        
    Returns:
        List of field names missing values
    """
```

### Usage Examples

```python
# Create report for task tracking
report = Report(template_name="summarization_tasks")

# Create task form
form = report.create_form(
    assignment="text -> summary",
    task_description="Summarize given text",
    fill_inputs=True  # Copy report values to form
)

# Process form
form.fill_request_fields(summary="Summarized text...")

# Save completed form
if form.is_completed():
    report.save_completed_form(
        form,
        update_results=True  # Copy results to report
    )

# Check remaining work
incomplete = report.get_incomplete_fields()
```

## Form-Report Interaction

The typical workflow involves:

1. Report manages overall task tracking
2. Creates forms for individual tasks
3. Forms process specific inputs/outputs
4. Report collects completed forms and results

```python
# Setup task tracking
report = Report(template_name="data_processing")

# Process multiple items
for item in data_items:
    # Create form for item
    form = report.create_form(
        assignment="data -> processed",
        task_description="Process data item"
    )
    
    # Fill and process
    form.fill_input_fields(data=item)
    result = process_data(form.instruction_dict)
    form.fill_request_fields(processed=result)
    
    # Save back to report
    report.save_completed_form(form, update_results=True)

# Check completion
remaining = report.get_incomplete_fields()
```
