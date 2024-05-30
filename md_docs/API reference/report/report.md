
### Class: `Report`

**Parent Class:** [[Base Form#^f8937b|BaseForm]]

**Description**:
`Report` extends `BaseForm` to handle a collection of `Form` instances based on specific assignments, managing a pile of forms and ensuring synchronization and proper configuration.

#### Attributes:
- `forms` (Pile[Form]): A pile of forms related to the report.
- `form_assignments` (list): Assignments for the report.
- `form_template` (Type[Form]): The template for the forms in the report.

### `__init__`

**Signature**:
```python
def __init__(self, **kwargs):
```

**Parameters**:
- `**kwargs`: Additional keyword arguments for initializing the report.

**Description**:
Initializes the `Report` with input and requested fields based on the report's assignment, creating forms dynamically from provided assignments.

### `work_fields`

**Signature**:
```python
@property
def work_fields(self) -> dict[str, Any]:
```

**Return Values**:
- `dict[str, Any]`: A dictionary of all work fields from all forms in the report.

**Description**:
Retrieves a dictionary of the fields relevant to the current task, combining the work fields from all forms in the report.

### `fill`

**Signature**:
```python
def fill(self, form: Form | list[Form] | dict[Form] = None, strict=True, **kwargs):
```

**Parameters**:
- `form` (Form | list[Form] | dict[Form], optional): The form(s) to fill from.
- `strict` (bool, optional): Whether to enforce strict filling. Defaults to True.
- `**kwargs`: Additional fields to fill.

**Description**:
Fills the report from another form instance, a list of forms, or provided keyword arguments. Raises an error if the report is already filled.

### `is_workable`

**Signature**:
```python
def is_workable(self) -> bool:
```

**Return Values**:
- `bool`: True if the report is workable, otherwise raises `ValueError`.

**Description**:
Checks if the report is ready for processing, ensuring all necessary fields are filled and output fields are unique across forms.

### `next_forms`

**Signature**:
```python
def next_forms(self) -> Pile[Form]:
```

**Return Values**:
- `Pile[Form]`: A pile of workable forms or None if there are no workable forms.

**Description**:
Returns a pile of workable forms based on current form states within the report.

**Usage Examples**:
```python
# Initialize a report with form assignments
report = Report(assignment="input1, input2 -> output", form_assignments=["a, b -> c", "c -> d", "d -> e"])

# Add values to input fields
report.fill(input1="value1", input2="value2")

# Check if the report is workable
if report.is_workable():
    print("Report is workable.")

# Display next forms to be processed
next_forms = report.next_forms()
if next_forms:
    for form in next_forms:
        form.display()
```
