
### Class: `Rule`

**Description**:
`Rule` combines a condition and an action that can be applied based on it. It includes methods to log applications, determine if the rule applies, invoke the rule's logic, and perform fixes if necessary.

#### Attributes:
- `apply_type` (list[str] | str | None): The type of data to which the rule applies.
- `fix` (bool): Indicates whether the rule includes a fix action.
- `fields` (list[str]): List of fields to which the rule applies.
- `validation_kwargs` (dict): Keyword arguments for validation.
- `applied_log` (list): Log of applied rules.
- `invoked_log` (list): Log of invoked rules.
- `_is_init` (bool): Indicates whether the rule is initialized.
- `exclude_type` (list[str]): List of types to exclude from rule application.

### Method: `__init__`

**Signature**:
```python
def __init__(self, apply_type="rule", fix=True, **kwargs):
```

**Parameters**:
- `apply_type` (str): The type of data to which the rule applies. Default is `"rule"`.
- `fix` (bool, optional): Indicates whether the rule includes a fix action. Default is `True`.
- `**kwargs`: Additional keyword arguments for initialization.

**Description**:
Initializes the `Rule` with the specified type and fix behavior.

### Method: `add_log`

**Signature**:
```python
def add_log(self, field: str, form: Any, apply: bool = True, **kwargs) -> None:
```

**Parameters**:
- `field` (str): The field being validated.
- `form` (Any): The form being validated.
- `apply` (bool, optional): Indicates whether the log is for an applied rule. Default is `True`.
- `**kwargs`: Additional configuration parameters.

**Description**:
Adds an entry to the applied or invoked log.

### Method: `applies`

**Signature**:
```python
async def applies(
    self,
    field: str,
    value: Any,
    form: Any,
    *args,
    annotation: List[str] = None,
    use_annotation: bool = True,
    **kwargs,
) -> bool:
```

**Parameters**:
- `field` (str): The field being validated.
- `value` (Any): The value of the field.
- `form` (Any): The form being validated.
- `annotation` (list[str], optional): Annotations for the field.
- `use_annotation` (bool): Indicates whether to use annotations. Default is `True`.
- `*args`: Additional arguments.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `bool`: True if the rule applies, otherwise False.

**Description**:
Determines whether the rule applies to a given field and value.

### Method: `invoke`

**Signature**:
```python
async def invoke(self, field: str, value: Any, form: Any) -> Any:
```

**Parameters**:
- `field` (str): The field being validated.
- `value` (Any): The value of the field.
- `form` (Any): The form being validated.

**Return Values**:
- `Any`: The validated or fixed value.

**Exceptions Raised**:
- `FieldError`: If validation or fixing fails.

**Description**:
Invokes the rule's validation logic on a field and value.

### Method: `rule_condition`

**Signature**:
```python
async def rule_condition(self, field, value, *args, **kwargs) -> bool:
```

**Parameters**:
- `field` (str): The field being validated.
- `value` (Any): The value of the field.
- `*args`: Additional arguments.
- `**kwargs`: Additional keyword arguments.

**Return Values**:
- `bool`: False by default, should be overridden by subclasses.

**Description**:
Defines an additional condition, if choosing not to use annotation as a qualifier. By default, returns `False`.

### Method: `perform_fix`

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
- `ValueError`: If the fix fails.

**Description**:
Attempts to fix a value if validation fails. By default, returns the value unchanged.

### Method: `validate`

**Signature**:
```python
async def validate(self, value: Any) -> Any:
```

**Parameters**:
- `value` (Any): The value to validate.

**Return Values**:
- `Any`: The validated value.

**Exceptions Raised**:
- `ValueError`: If validation fails.

**Description**:
Abstract method to validate a value. Must be implemented by subclasses.

### Method: `_to_dict`

**Signature**:
```python
def _to_dict(self) -> Dict[str, Any]:
```

**Return Values**:
- `dict`: A dictionary representation of the rule.

**Description**:
Converts the rule's attributes to a dictionary.

### Method: `__str__`

**Signature**:
```python
def __str__(self) -> str:
```

**Return Values**:
- `str`: A string representation of the rule.

**Description**:
Returns a string representation of the rule using a pandas `Series`.

### Method: `__repr__`

**Signature**:
```python
def __repr__(self) -> str:
```

**Return Values**:
- `str`: A string representation of the rule.

**Description**:
Returns a string representation of the rule using a pandas `Series`.

**Usage Examples**:
```python
# Example 1: Creating a rule and checking if it applies
rule = Rule(apply_type="text", fields=["name", "description"])
form = Form(name="example")
result = await rule.applies(field="name", value="example", form=form)
print(result)  # Output: True

# Example 2: Invoking a rule's validation logic
validated_value = await rule.invoke(field="name", value="example", form=form)
print(validated_value)  # Output: "example"

# Example 3: Using rule's string representation
print(rule)  # Output: pandas Series representation of the rule's attributes
```
