
### Class: `SelectTemplate`

**Description**:
`SelectTemplate` is a specialized class extending `BaseUnitForm` to handle selection tasks based on given instructions and context. It includes fields for specifying the selection, the choices, confidence scoring, and reasoning.

### Attributes:

- **confidence_score** (`float | None`): A numeric score between 0 to 1 formatted to 2 decimal places, indicating confidence in the selection.
- **reason** (`str | None`): A brief reason for the given output.
- **template_name** (`str`): The name of the template. Defaults to `"default_select"`.
- **selection** (`Enum | str | list | None`): The selection from given choices.
- **choices** (`list`): The given choices to select from.
- **assignment** (`str`): A string representing the task assignment for the selection. Defaults to `"task -> selection"`.

### Fields:

#### `confidence_score`

**Type**: `float | None`

**Description**:
A numeric score between 0 to 1 formatted in `num:0.2f`, where 1 indicates very confident and 0 indicates not confident at all.

**Validation_kwargs**:
- `upper_bound`: 1
- `lower_bound`: 0
- `num_type`: `float`
- `precision`: 2

#### `reason`

**Type**: `str | None`

**Description**:
A brief reason for the given output, formatted as "This is my best response because ...".

#### `selection`

**Type**: `Enum | str | list | None`

**Description**:
The selection from given choices.

#### `choices`

**Type**: `list`

**Description**:
The given choices to select from.

#### `assignment`

**Type**: `str`

**Description**:
A string representing the task assignment for the selection.

**Default**: `"task -> selection"`

### Methods:

#### `answer`

**Description**:
Gets the `selection` attribute.

**Returns**:
- `Enum | str | list | None`: The selection from given choices.

#### `__init__`

**Description**:
Initializes a new instance of the `SelectTemplate` class.

**Args**:
- `instruction` (`str`, optional): Additional instructions for the selection task.
- `context` (`str`, optional): Additional context for the selection task.
- `choices` (`list`, optional): The choices to select from.
- `reason` (`bool`, optional): Whether to include a reasoning field. Defaults to `False`.
- `confidence_score` (`bool`, optional): Whether to include a confidence score. Defaults to `False`.
- `**kwargs`: Additional keyword arguments.

### Example Usage:

```python
# Create an instance of SelectTemplate with optional instruction, context, and choices
select_template = SelectTemplate(
    instruction="Choose the best option",
    context="Based on the recent performance metrics",
    choices=["Option A", "Option B", "Option C"],
    reason=True,
    confidence_score=True
)

# Fill the form with a selection and other details
select_template.fill(
    selection="Option B",
    reason="Option B has the highest performance metrics.",
    confidence_score=0.95
)

# Check if the form is filled and ready to use
if select_template.filled:
    print("SelectTemplate is filled and ready to use.")
else:
    print("SelectTemplate is not filled yet.")
```

This class provides a structured way to handle selection tasks, ensuring necessary fields are filled and validated according to the provided instructions and context. It also allows for the inclusion of confidence scoring and reasoning if needed.
