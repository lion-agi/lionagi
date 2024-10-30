
### Class: `PredictTemplate`

**Description**:
`PredictTemplate` is a specialized class extending `BaseUnitForm` to facilitate predictions of the next sentence(s) based on given instructions and context. It includes fields for specifying the number of sentences to predict, confidence scoring, and reasoning.

### Attributes:

- **confidence_score** (`float | None`): A numeric score between 0 to 1 formatted to 2 decimal places, indicating confidence in the prediction.
- **reason** (`str | None`): A brief reason for the given output.
- **template_name** (`str`): The name of the template. Defaults to `"predict_template"`.
- **num_sentences** (`int`): The number of sentences to predict. Defaults to `2`.
- **prediction** (`None | str | list`): The predicted sentence(s) or desired output.
- **assignment** (`str`): A string representing the task assignment for the prediction. Defaults to `"task -> prediction"`.

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

#### `num_sentences`

**Type**: `int`

**Description**:
The number of sentences to predict.

**Default**: `2`

#### `prediction`

**Type**: `None | str | list`

**Description**:
The predicted sentence(s) or desired output.

#### `assignment`

**Type**: `str`

**Description**:
A string representing the task assignment for the prediction.

**Default**: `"task -> prediction"`

### Methods:

#### `answer`

**Description**:
Gets the `prediction` attribute.

**Returns**:
- `None | str | list`: The predicted sentence(s) or desired output.

#### `__init__`

**Description**:
Initializes a new instance of the `PredictTemplate` class.

**Args**:
- `instruction` (`str`, optional): Additional instructions for the prediction.
- `context` (`str`, optional): Additional context for the prediction.
- `num_sentences` (`int`, optional): The number of sentences to predict. Defaults to `2`.
- `confidence_score` (`bool`, optional): Whether to include a confidence score. Defaults to `False`.
- `reason` (`bool`, optional): Whether to include a reasoning field. Defaults to `False`.
- `**kwargs`: Additional keyword arguments.

### Example Usage:

```python
# Create an instance of PredictTemplate with optional instruction and context
predict_template = PredictTemplate(
    instruction="Predict the next steps in the project",
    context="The project involves developing a new AI model.",
    num_sentences=3,
    confidence_score=True,
    reason=True
)

# Fill the form with a prediction and other details
predict_template.fill(prediction=[
    "First, gather all the relevant data for the project.",
    "Next, preprocess the data to ensure quality and consistency.",
    "Finally, start building and training the AI model using the preprocessed data."
])

# Check if the form is filled and ready to use
if predict_template.filled:
    print("PredictTemplate is filled and ready to use.")
else:
    print("PredictTemplate is not filled yet.")
```

This class provides a structured way to handle predictions of sentences, ensuring necessary fields are filled and validated according to the provided instructions and context. It also allows for the inclusion of confidence scoring and reasoning if needed.
