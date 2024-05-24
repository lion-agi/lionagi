
### Class: `PlanTemplate`

**Description**:
`PlanTemplate` extends the `BaseUnitForm` class, providing a template for generating a step-by-step plan based on given instructions and context. This class is designed to facilitate the creation of detailed plans with reasoning and confidence scoring.

### Attributes:

- **template_name** (`str`): The name of the template. Defaults to `"plan_template"`.
- **plan** (`dict | str`): The generated step-by-step plan, returned as a dictionary following the `{step_n: {plan: ..., reason: ...}}` format.
- **signature** (`str`): A string representing the task signature for the plan. Defaults to `"task -> plan"`.

### Fields:

#### `plan`

**Type**: `dict | str`

**Description**:
The generated step-by-step plan, returned as a dictionary following the `{step_n: {plan: ..., reason: ...}}` format.

**Default**: `default_factory=dict`

#### `signature`

**Type**: `str`

**Description**:
A string representing the task signature for the plan.

**Default**: `"task -> plan"`

### Methods:

#### `answer`

**Description**:
Gets the `plan` attribute.

**Returns**:
- `dict | str`: The generated plan.

#### `__init__`

**Description**:
Initializes a new instance of the `PlanTemplate` class.

**Args**:
- `instruction` (`str`, optional): Additional instructions for the plan.
- `context` (`str`, optional): Additional context for the plan.
- `confidence_score` (`bool`, optional): Whether to include a confidence score.
- `reason` (`bool`, optional): Whether to include a reasoning field.
- `num_step` (`int`, optional): The number of steps in the plan. Defaults to `3`.
- `**kwargs`: Additional keyword arguments.

### Example Usage:

```python
# Create an instance of PlanTemplate with optional instruction and context
plan_template = PlanTemplate(
    instruction="Develop a new feature",
    context="Feature must be scalable and user-friendly",
    confidence_score=True,
    reason=True,
    num_step=5
)

# Fill the form with a plan and other details
plan_template.fill(plan={
    "step_1": {
        "plan": "Analyze user requirements",
        "reason": "Understanding user needs is essential for developing relevant features."
    },
    "step_2": {
        "plan": "Design the feature architecture",
        "reason": "A well-planned architecture ensures scalability and maintainability."
    },
    "step_3": {
        "plan": "Develop the feature",
        "reason": "Implement the design using appropriate technologies."
    },
    "step_4": {
        "plan": "Test the feature",
        "reason": "Testing ensures the feature works as expected and is free of bugs."
    },
    "step_5": {
        "plan": "Deploy the feature",
        "reason": "Deployment makes the feature available to users."
    }
})

# Check if the form is filled and ready to use
if plan_template.filled:
    print("PlanTemplate is filled and ready to use.")
else:
    print("PlanTemplate is not filled yet.")
```

This class provides a structured way to handle the generation of step-by-step plans, ensuring that necessary fields are filled and validated according to the provided instructions and context. It also allows for the inclusion of confidence scoring and reasoning if needed.
