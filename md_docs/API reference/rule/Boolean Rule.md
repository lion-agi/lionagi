
### Class: `BooleanRule`

**Parent Class:** [[Base Rule#^34c3a1|Rule]]

**Description**:
`BooleanRule` is a specific implementation of the `Rule` class that validates and fixes boolean values. It ensures that a given value is a valid boolean and attempts to convert non-boolean values to booleans if they can be interpreted as such.

#### Attributes:
- `fields` (list[str]): List of fields to which the rule applies. Default is `["action_required"]`.
- `apply_type` (str): The type of data to which the rule applies. Default is `"bool"`.

### `__init__`

**Signature**:
```python
def __init__(self, apply_type="bool", **kwargs):
```

**Parameters**:
- `apply_type` (str): The type of data to which the rule applies. Default is `"bool"`.
- `**kwargs`: Additional keyword arguments for initialization.

**Description**:
Initializes the `BooleanRule` with the specified type and additional keyword arguments.

### `validate`

**Signature**:
```python
async def validate(self, value: Any) -> bool:
```

**Parameters**:
- `value` (Any): The value to validate.

**Return Values**:
- `bool`: The validated value.

**Exceptions Raised**:
- `ValueError`: If the value is not a valid boolean.

**Description**:
Validates that the given value is a boolean.

### `perform_fix`

**Signature**:
```python
async def perform_fix(self, value: Any) -> bool:
```

**Parameters**:
- `value` (Any): The value to fix.

**Return Values**:
- `bool`: The fixed value.

**Exceptions Raised**:
- `ValueError`: If the value cannot be converted to a boolean.

**Description**:
Attempts to fix the given value by converting it to a boolean. Recognizes strings like "true", "1", "yes" as `True` and "false", "0", "no" as `False`.

**Usage Examples**:
```python
# Example 1: Creating a BooleanRule and validating a value
boolean_rule = BooleanRule()
validated_value = await boolean_rule.validate(True)
print(validated_value)  # Output: True

# Example 2: Attempting to validate an invalid value
try:
    validated_value = await boolean_rule.validate("yes")
except ValueError as e:
    print(e)  # Output: Invalid boolean value.

# Example 3: Fixing a non-boolean value
fixed_value = await boolean_rule.perform_fix("yes")
print(fixed_value)  # Output: True

# Example 4: Handling an invalid value that cannot be fixed
try:
    fixed_value = await boolean_rule.perform_fix("unknown")
except ValueError as e:
    print(e)  # Output: Failed to convert unknown into a boolean value
```
