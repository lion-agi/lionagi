
### Class: `ScoreTemplate`

**Description**:
`ScoreTemplate` is a specialized class extending `UnitForm` to handle scoring tasks based on given instructions and context. It includes fields for specifying the score, confidence scoring, and reasoning.

### Attributes:

- **confidence_score** (`float | None`): A numeric score between 0 to 1 formatted to 2 decimal places, indicating confidence in the score.
- **reason** (`str | None`): A brief reason for the given output.
- **template_name** (`str`): The name of the template. Defaults to `"score_template"`.
- **score** (`float | None`): A score for the given context and task.
- **assignment** (`str`): A string representing the task assignment for the score. Defaults to `"task -> score"`.

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

#### `score`

**Type**: `float | None`

**Description**:
A numeric score for the given context and task.

#### `assignment`

**Type**: `str`

**Description**:
A string representing the task assignment for the score.

**Default**: `"task -> score"`

### Methods:

#### `answer`

**Description**:
Gets the `score` attribute.

**Returns**:
- `float | None`: The score for the given context and task.

#### `__init__`

**Description**:
Initializes a new instance of the `ScoreTemplate` class.

**Args**:
- `instruction` (`str`, optional): Additional instructions for the scoring task.
- `context` (`str`, optional): Additional context for the scoring task.
- `score_range` (`tuple`, optional): The range of the score. Defaults to `(0, 10)`.
- `include_endpoints` (`bool`, optional): Whether to include the endpoints in the score range. Defaults to `True`.
- `num_digit` (`int`, optional): The number of digits allowed after the decimal point. Defaults to `0`.
- `confidence_score` (`bool`, optional): Whether to include a confidence score. Defaults to `False`.
- `reason` (`bool`, optional): Whether to include a reasoning field. Defaults to `False`.
- `**kwargs`: Additional keyword arguments.

### Example Usage:

```python
# Create an instance of ScoreTemplate with optional instruction and context
score_template = ScoreTemplate(
    instruction="Evaluate the performance of the new AI model",
    context="The model was trained on the latest dataset and showed improvement in accuracy.",
    score_range=(0, 100),
    include_endpoints=True,
    num_digit=2,
    confidence_score=True,
    reason=True
)

# Fill the form with a score and other details
score_template.fill(score=92.5, reason="The model performed well with significant improvements in accuracy.")

# Check if the form is filled and ready to use
if score_template.filled:
    print("ScoreTemplate is filled and ready to use.")
else:
    print("ScoreTemplate is not filled yet.")
```

This class provides a structured way to handle scoring tasks, ensuring necessary fields are filled and validated according to the provided instructions and context. It also allows for the inclusion of confidence scoring and reasoning if needed.
