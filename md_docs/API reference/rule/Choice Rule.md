
### Class: `ChoiceRule`

^15d16d

**Parent Class:** [[Base Rule#^34c3a1|Rule]]

**Description**:
`ChoiceRule` is a specific implementation of the `Rule` class that validates if a given value is within a predefined set of choices. It also provides a method to suggest the most similar valid choice if the given value is invalid.

#### Attributes:
- `apply_type` (str): The type of data to which the rule applies. Default is `"enum"`.
- `keys` (list): The list of valid choices.

### `__init__`

**Signature**:
```python
def __init__(self, apply_type="enum", **kwargs):
```

**Parameters**:
- `apply_type` (str): The type of data to which the rule applies. Default is `"enum"`.
- `**kwargs`: Additional keyword arguments for initialization.

**Description**:
Initializes the `ChoiceRule` with the specified type and additional keyword arguments, including the list of valid choices.

### `validate`

**Signature**:
```python
async def validate(self, value: str, *args, **kwargs) -> str:
```

**Parameters**:
- `value` (str): The value to validate.
- `*args`: Additional arguments.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `str`: The validated value.

**Exceptions Raised**:
- `ValueError`: If the value is not in the set of choices.

**Description**:
Validates that the given value is within the set of predefined choices.

### `perform_fix`

**Signature**:
```python
async def perform_fix(self, value) -> str:
```

**Parameters**:
- `value` (str): The value to suggest a fix for.

**Return Values**:
- `str`: The most similar value from the set of predefined choices.

**Description**:
Suggests a fix for a value that is not within the set of predefined choices by returning the most similar valid choice.

**Usage Examples**:
```python
# Example 1: Creating a ChoiceRule and validating a value
choices = ["apple", "banana", "cherry"]
choice_rule = ChoiceRule(validation_kwargs={"keys": choices})
validated_value = await choice_rule.validate("banana")
print(validated_value)  # Output: banana

# Example 2: Attempting to validate an invalid value
try:
    validated_value = await choice_rule.validate("grape")
except ValueError as e:
    print(e)  # Output: grape is not in choices ['apple', 'banana', 'cherry']

# Example 3: Fixing a non-valid value by suggesting the most similar choice
fixed_value = await choice_rule.perform_fix("grap")
print(fixed_value)  # Output: grape (assuming 'grape' is the most similar valid choice)
```
