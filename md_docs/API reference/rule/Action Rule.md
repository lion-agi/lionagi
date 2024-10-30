
### Class: `ActionRequestRule`

**Parent Class:** [[mapping#^ec2bae|MappingRule]]

**Description**:
`ActionRequestRule` is a validation and fixing rule for action requests, extending from `MappingRule`. It validates and attempts to fix action requests, discarding invalid ones based on the provided configuration.

#### Attributes:
- `discard` (bool): Indicates whether to discard invalid action requests.

### `__init__`

**Signature**:
```python
def __init__(self, apply_type="actionrequest", discard=True, **kwargs):
```

**Parameters**:
- `apply_type` (str): The type of data to which the rule applies. Default is `"actionrequest"`.
- `discard` (bool, optional): Indicates whether to discard invalid action requests. Default is `True`.
- `**kwargs`: Additional keyword arguments for initialization.

**Description**:
Initializes the `ActionRequestRule` with the specified type and discard behavior.

### `validate`

**Signature**:
```python
async def validate(self, value):
```

**Parameters**:
- `value` (Any): The value of the action request to validate.

**Return Values**:
- `Any`: The validated action request.

**Exceptions Raised**:
- `ActionError`: If the action request is invalid.

**Description**:
Validates the action request to ensure it contains at least the keys "function" and "arguments".

### `perform_fix`

**Signature**:
```python
async def perform_fix(self, value):
```

**Parameters**:
- `value` (Any): The value of the action request to fix.

**Return Values**:
- `Any`: The fixed action request.

**Exceptions Raised**:
- `ActionError`: If the action request cannot be fixed.

**Description**:
Attempts to fix an invalid action request by converting it to a list of dictionaries and ensuring each dictionary contains at least the keys "function" and "arguments". If the action request cannot be fixed and `discard` is set to `False`, an error is raised.

**Usage Examples**:
```python
# Example 1: Initializing and validating an action request
rule = ActionRequestRule(discard=False)
valid_action_request = {
    "function": "example_function",
    "arguments": {"param1": "value1"}
}
validated_request = await rule.validate(valid_action_request)
print(validated_request)  # Output: {'function': 'example_function', 'arguments': {'param1': 'value1'}}

# Example 2: Fixing an invalid action request
invalid_action_request = '{"function": "example_function", "args": {"param1": "value1"}}'
fixed_request = await rule.perform_fix(invalid_action_request)
print(fixed_request)  # Output: [{'function': 'example_function', 'arguments': {'param1': 'value1'}}]

# Example 3: Handling an invalid action request with discard set to True
try:
    rule_with_discard = ActionRequestRule(discard=True)
    invalid_request = {"invalid_key": "value"}
    await rule_with_discard.validate(invalid_request)
except ActionError as e:
    print(e)  # Output: Invalid action request: {'invalid_key': 'value'}
```

### Enum: `ActionRequestKeys`

**Description**:
An enumeration to store keys for action requests for consistent referencing.

**Values**:
- `FUNCTION`: Represents the "function" key.
- `ARGUMENTS`: Represents the "arguments" key.

**Usage Examples**:
```python
# Accessing enum values
print(ActionRequestKeys.FUNCTION.value)  # Output: 'function'
print(ActionRequestKeys.ARGUMENTS.value)  # Output: 'arguments'
```
