
### Class: `BaseUnitForm`

**Description**:
`BaseUnitForm` is a specialized form class designed for units that includes additional fields for confidence scoring and reasoning. It extends the `Form` class and provides mechanisms for scoring confidence levels and providing reasoned explanations.

### Attributes:

- `template_name` (str): The name of the template. Defaults to `"UnitDirective"`.
- `confidence_score` (float): A numeric confidence score between 0 and 1 with precision to 2 decimal places.
- `reason` (str | None): A field for providing concise reasoning for the process.

### Fields:

#### `confidence_score`

**Type**: `float`

**Description**:
Provide a numeric confidence score on how likely you successfully achieved the task between 0 and 1, with precision to 2 decimal places. 1 being very confident in a good job, 0 is not confident at all.

**Validation Keywords**:
- `upper_bound`: 1
- `lower_bound`: 0
- `num_type`: `float`
- `precision`: 2

#### `reason`

**Type**: `str | None`

**Description**:
Explain yourself, provide concise reasoning for the process. Must start with: "Let's think step by step".

### Example Usage

```python
# Create an instance of BaseUnitForm
unit_form = BaseUnitForm(
    confidence_score=0.85,
    reason="Let's think step by step, the process was followed as planned."
)

# Validate and process the form
if unit_form.filled:
    print("Form is filled and ready to use.")
else:
    print("Form is not filled yet.")
```

This class provides a structure for forms that require a confidence score and a reason, ensuring that inputs are validated and processed correctly. The confidence score must be a float between 0 and 1, and the reason must begin with a specific phrase, promoting consistency in responses.
