
### Class: `Form`

**Parent Class:** [[Base Form#^f8937b|BaseForm]]

**Description**:
`Form` is a specialized implementation of `BaseForm` designed to manage form fields dynamically based on specified assignments. It supports initialization and management of input and requested fields, handles form filling operations, and ensures forms are properly configured for use.

#### Attributes:
- `input_fields` (List[str]): Fields required to carry out the objective of the form.
- `requested_fields` (List[str]): Fields requested to be filled by the user.

### `__init__`

**Signature**:
```python
def __init__(self, **kwargs):
```

**Parameters**:
- `**kwargs`: Additional keyword arguments passed to initialize the form.

**Description**:
Initializes a new instance of the `Form`, setting up input and requested fields based on the form's assignment.

### `append_to_request`

**Signature**:
```python
def append_to_request(self, field: str, value=None):
```

**Parameters**:
- `field` (str): The name of the field to be requested.
- `value` (optional): The value to be assigned to the field. Defaults to None.

**Description**:
Appends a field to the requested fields.

### `append_to_input`

**Signature**:
```python
def append_to_input(self, field: str, value=None):
```

**Parameters**:
- `field` (str): The name of the field to be added to input.
- `value` (optional): The value to be assigned to the field. Defaults to None.

**Description**:
Appends a field to the input fields.

### `work_fields`

**Signature**:
```python
@property
def work_fields(self) -> Dict[str, Any]:
```

**Return Values**:
- `Dict[str, Any]`: The relevant fields for the current task.

**Description**:
Retrieves a dictionary of the fields relevant to the current task, excluding any `SYSTEM_FIELDS` and including only the input and requested fields.

### `fill`

**Signature**:
```python
def fill(self, form: "Form" = None, strict: bool = True, **kwargs) -> None:
```

**Parameters**:
- `form` (Form, optional): The form to fill from.
- `strict` (bool, optional): Whether to enforce strict filling. Defaults to True.
- `**kwargs`: Additional fields to fill.

**Description**:
Fills the form from another form instance or provided keyword arguments. Raises an error if the form is already filled.

### `is_workable`

**Signature**:
```python
def is_workable(self) -> bool:
```

**Return Values**:
- `bool`: True if the form is workable, otherwise raises `ValueError`.

**Description**:
Determines if the form is ready for processing. Checks if all required fields are filled and raises an error if the form is already filled or if any required field is missing.

### `_instruction_context`

**Signature**:
```python
@property
def _instruction_context(self) -> str:
```

**Return Values**:
- `str`: A detailed description of the input fields.

**Description**:
Generates a detailed description of the input fields, including their current values and descriptions.

### `_instruction_prompt`

**Signature**:
```python
@property
def _instruction_prompt(self) -> str:
```

**Return Values**:
- `str`: The instruction prompt for the form.

**Description**:
Generates a prompt for task instructions, describing the task, input fields, and requested output fields.

### `_instruction_requested_fields`

**Signature**:
```python
@property
def _instruction_requested_fields(self) -> Dict[str, str]:
```

**Return Values**:
- `Dict[str, str]`: A dictionary of requested field descriptions.

**Description**:
Provides a dictionary mapping requested field names to their descriptions.

### `display`

**Signature**:
```python
def display(self, fields=None):
```

**Parameters**:
- `fields` (optional): Specific fields to display. Defaults to None.

**Description**:
Displays the form fields using IPython display.

**Usage Examples**:
```python
form = Form(assignment="input1, input2 -> output", task="Sample task")
form.append_to_input("input1", "value1")
form.append_to_request("output")
print(form.work_fields)  # Output: {'input1': 'value1', 'output': None}

form.fill(input2="value2")
print(form.filled)  # Output: True

if form.is_workable():
    form.display()
```
