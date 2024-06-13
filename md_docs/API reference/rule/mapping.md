
### Class: `MappingRule`

^ec2bae

**Parent Class:** [[Choice Rule#^15d16d|ChoiceRule]]

**Description**:
`MappingRule` is a specific implementation of the `Rule` class that validates if a given value is a dictionary (mapping) with specific keys. It also provides a method to attempt to fix the value if it does not initially meet the validation criteria.

#### Attributes:
- `apply_type` (str): The type of data to which the rule applies. Default is `"dict"`.
- `keys` (list): The list of specific keys that the mapping must contain.

### `__init__`

**Signature**:
```python
def __init__(self, apply_type="dict", **kwargs):
```

**Parameters**:
- `apply_type` (str): The type of data to which the rule applies. Default is `"dict"`.
- `**kwargs`: Additional keyword arguments for initialization.

**Description**:
Initializes the `MappingRule` with the specified type and additional keyword arguments, including the list of specific keys that the mapping must contain.

### `validate`

**Signature**:
```python
async def validate(self, value: Any, *args, **kwargs) -> Any:
```

**Parameters**:
- `value` (Any): The value to validate.
- `*args`: Additional arguments.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `Any`: The validated value.

**Exceptions Raised**:
- `ValueError`: If the value is not a valid mapping or has incorrect keys.

**Description**:
Validates that the given value is a dictionary with the specified keys.

### `perform_fix`

**Signature**:
```python
async def perform_fix(self, value: Any, *args, **kwargs) -> Any:
```

**Parameters**:
- `value` (Any): The value to fix.
- `*args`: Additional arguments.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `Any`: The fixed value.

**Exceptions Raised**:
- `ValueError`: If the value cannot be fixed.

**Description**:
Attempts to fix the value by converting it to a dictionary and ensuring it has the correct keys. If the keys do not match, it suggests the most similar valid keys.

**Usage Examples**:
```python
# Example 1: Creating a MappingRule and validating a value
keys = ["name", "age"]
mapping_rule = MappingRule(validation_kwargs={"keys": keys})
validated_value = await mapping_rule.validate({"name": "Alice", "age": 30})
print(validated_value)  # Output: {'name': 'Alice', 'age': 30}

# Example 2: Attempting to validate an invalid value
try:
    validated_value = await mapping_rule.validate({"name": "Alice"})
except ValueError as e:
    print(e)  # Output: Invalid mapping keys. Current keys ['name'] != ['name', 'age']

# Example 3: Fixing a non-valid value by suggesting the most similar keys
fixed_value = await mapping_rule.perform_fix({"name": "Alice", "years": 30})
print(fixed_value)  # Output: {'name': 'Alice', 'age': 30} (assuming 'years' is corrected to 'age')
```
