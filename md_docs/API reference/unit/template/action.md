
### Class: `ActionTemplate`

**Description**:
`ActionTemplate` extends the `BaseUnitForm` class, providing a template for actions that includes instructions, context, and confidence scoring. This class is designed to facilitate the reasoning and preparation of actions based on given tools and additional inputs.

### Attributes:

- **action_required** (`bool | None`): Indicates if actions are required.
- **actions** (`list[dict] | None`): A list of actions to take, formatted as dictionaries.
- **answer** (`str | None`): The output answer to the questions asked.
- **assignment** (`str`): The assignment structure for the task. Defaults to `"task -> reason, action_required, actions, answer"`.

### Fields:

#### `action_required`

**Type**: `bool | None`

**Description**:
Set to `True` if actions are required. Provide actions if `True`.

#### `actions`

**Type**: `list[dict] | None`

**Description**:
A list of actions to take. Format: `[{'function': func, 'arguments': {'param1':..., 'param2':...}}]`. Leave blank if no actions are needed. Must use provided functions and parameters, do not make up names. Flag `action_required` as `True` if filled.

#### `answer`

**Type**: `str | None`

**Description**:
Output answer to the questions asked if further actions are not needed. Leave blank if an accurate answer cannot be provided from context during this step.

#### `assignment`

**Type**: `str`

**Description**:
The assignment structure for the task. Defaults to `"task -> reason, action_required, actions, answer"`.

### Methods:

#### `__init__`

**Description**:
Initializes an instance of the `ActionTemplate` class.

**Args**:
- `instruction` (`str`, optional): Additional instruction for the task.
- `context` (`str`, optional): Additional context for the task.
- `confidence_score` (`bool`, optional): If `True`, includes confidence scoring.
- `**kwargs`: Additional keyword arguments.

**Example Usage**:

```python
# Create an instance of ActionTemplate with optional instruction and context
action_template = ActionTemplate(
    instruction="Analyze the data",
    context="Data provided by the user",
    confidence_score=True
)

# Fill the form with actions and other details
action_template.fill(actions=[
    {
        "function": "analyze_data",
        "arguments": {
            "data": "sample data",
            "threshold": 0.8
        }
    }
], answer="The analysis is complete with the given data.")

# Check if the form is filled and ready to use
if action_template.filled:
    print("ActionTemplate is filled and ready to use.")
else:
    print("ActionTemplate is not filled yet.")
```

This class provides a structured way to handle actions and reasoning, ensuring that necessary fields are filled and validated according to the provided instructions and context. It also allows for confidence scoring to be included if needed.
