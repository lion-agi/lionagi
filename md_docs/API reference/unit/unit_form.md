
### Class: `UnitForm`

**Description**:
`UnitForm` is a specialized form for managing unit directives and outputs. It includes fields for actions, answers, predictions, plans, scores, and reflections, among others, to handle complex unit operations.

### Attributes:

- `actions` (dict | None): Actions to take based on the context and instruction.
- `action_required` (bool | None): Set to `True` if actions are provided, else `False`.
- `answer` (str | None): Answer to the questions asked.
- `extension_required` (bool | None): Set to `True` if more steps are needed.
- `prediction` (str | None): Likely prediction based on context and instruction.
- `plan` (dict | str | None): Step-by-step plan.
- `next_steps` (dict | str | None): Ideas on next actions to take.
- `score` (float | None): Numeric performance score.
- `reflection` (str | None): Self-reflection on reasoning and performance.
- `selection` (Enum | str | list | None): A single item from the choices.
- `tool_schema` (list | dict | None): The list of tools available for use.
- `assignment` (str): Default assignment task description.

### Methods:

#### `__init__`

**Signature**:
```python
def __init__(
    self,
    instruction=None,
    context=None,
    reason: bool = True,
    predict: bool = False,
    score=True,
    select=None,
    plan=None,
    brainstorm=None,
    reflect=None,
    tool_schema=None,
    allow_action: bool = False,
    allow_extension: bool = False,
    max_extension: int = None,
    confidence=None,
    score_num_digits=None,
    score_range=None,
    select_choices=None,
    plan_num_step=None,
    predict_num_sentences=None,
    **kwargs,
):
```

**Parameters**:
- `instruction` (str | None): Additional instruction.
- `context` (str | None): Additional context.
- `reason` (bool): Flag to include reasoning.
- `predict` (bool): Flag to include prediction.
- `score` (bool): Flag to include score.
- `select` (Enum | str | list | None): Selection choices.
- `plan` (dict | str | None): Step-by-step plan.
- `brainstorm` (bool): Flag to include brainstorming next steps.
- `reflect` (bool): Flag to include self-reflection.
- `tool_schema` (list | dict | None): Schema of available tools.
- `allow_action` (bool): Allow actions to be added.
- `allow_extension` (bool): Allow extension for more steps.
- `max_extension` (int | None): Maximum number of extensions allowed.
- `confidence` (bool | None): Flag to include confidence score.
- `score_num_digits` (int | None): Number of decimal places for the score.
- `score_range` (list | None): Range for the score.
- `select_choices` (list | None): Choices for selection.
- `plan_num_step` (int | None): Number of steps in the plan.
- `predict_num_sentences` (int | None): Number of sentences for prediction.
- `kwargs`: Additional keyword arguments.

**Description**:
Initializes the `UnitForm` with various parameters and settings.

#### `display`

**Signature**:
```python
def display(self):
```

**Description**:
Displays the current form fields and values in a user-friendly format.

**Usage Examples**:
```python
# Initialize the form with some parameters
form = UnitForm(instruction="Analyze data", context="Dataset A")

# Display the form
form.display()
```

This example structure helps you understand how to document the `UnitForm` class and its methods, ensuring clarity and comprehensiveness.
