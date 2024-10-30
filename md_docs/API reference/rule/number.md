
### Class: `NumberRule`

**Parent Class:** [[Base Rule#^34c3a1|Rule]]

**Description**:
`NumberRule` is a rule for validating that a value is a number (either integer or float) within specified bounds. It inherits from the `Rule` class and provides methods for validation and fixing of numeric values.

#### Attributes:
- `apply_type` (str): The type of data to which the rule applies. Default is `"int, float"`.
- `upper_bound` (int | float | None): The upper bound for the value.
- `lower_bound` (int | float | None): The lower bound for the value.
- `num_type` (Type[int | float]): The type of number (int or float). Default is `float`.
- `precision` (int | None): The precision for floating point numbers.
- `fields` (list[str]): The fields to which the rule applies. Default is `["confidence_score", "score"]`.

### `__init__`

**Signature**:
```python
def __init__(self, apply_type="int, float", **kwargs):
```

**Parameters**:
- `apply_type` (str): The type of data to which the rule applies. Default is `"int, float"`.
- `**kwargs`: Additional keyword arguments for initialization.

**Description**:
Initializes the `NumberRule` with the specified type and additional keyword arguments, including upper and lower bounds, number type, and precision.

### `validate`

**Signature**:
```python
async def validate(self, value: Any) -> Any:
```

**Parameters**:
- `value` (Any): The value to validate.

**Return Values**:
- `Any`: The validated value.

**Exceptions Raised**:
- `ValueError`: If the value is not a valid number.

**Description**:
Validates that the given value is a number (either integer or float).

### `perform_fix`

**Signature**:
```python
async def perform_fix(self, value: Any) -> Any:
```

**Parameters**:
- `value` (Any): The value to fix.

**Return Values**:
- `Any`: The fixed value.

**Exceptions Raised**:
- `ValueError`: If the value cannot be converted to a number.

**Description**:
Attempts to fix the value by converting it to a number. If the value cannot be converted, it raises a `ValueError`.

**Usage Examples**:
```python
# Example 1: Creating a NumberRule and validating a value
number_rule = NumberRule(validation_kwargs={"upper_bound": 100, "lower_bound": 0})
validated_value = await number_rule.validate(50)
print(validated_value)  # Output: 50

# Example 2: Attempting to validate an invalid value
try:
    validated_value = await number_rule.validate("fifty")
except ValueError as e:
    print(e)  # Output: Invalid number field: fifty

# Example 3: Fixing a non-valid value by converting it to a number
fixed_value = await number_rule.perform_fix("50.5")
print(fixed_value)  # Output: 50.5
```
