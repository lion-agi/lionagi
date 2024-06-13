
### Class: `Validator`

**Description**:
`Validator` is a class to manage the validation of forms using a [[RuleBook#^fbf6db|RuleBook]]. It provides functionalities for initializing rules, validating fields, validating forms and reports, managing rules, and logging validation attempts and errors.

### Attributes:

- `_DEFAULT_RULEORDER` (List[str]): Default order of rule application.
- `_DEFAULT_RULES` (Dict\[str, [[Base Rule#^34c3a1|Rule]]\]): Default set of rules.

### Methods:

#### `__init__`

**Signature**:
```python
def __init__(
    self,
    *,
    rulebook: RuleBook = None,
    rules: Dict[str, Rule] = None,
    order: List[str] = None,
    init_config: Dict[str, Dict] = None,
    active_rules: Dict[str, Rule] = None,
)
```

**Parameters**:
- `rulebook` (RuleBook, optional): The `RuleBook` containing validation rules.
- `rules` (Dict[str, Rule], optional): Dictionary of validation rules.
- `order` (List[str], optional): List defining the order of rule application.
- `init_config` (Dict[str, Dict], optional): Configuration for initializing rules.
- `active_rules` (Dict[str, Rule], optional): Dictionary of currently active rules.

**Description**:
Initializes the `Validator`, setting up the `RuleBook`, active rules, and a validation log.

#### `_initiate_rules`

**Signature**:
```python
def _initiate_rules(self) -> Dict[str, Rule]
```

**Returns**:
- `dict`: A dictionary of active rules.

**Description**:
Initializes rules from the `RuleBook`.

#### `validate_field`

**Signature**:
```python
async def validate_field(
    self,
    field: str,
    value: Any,
    form: Form,
    *args,
    annotation=None,
    strict=True,
    use_annotation=True,
    **kwargs,
) -> Any
```

**Parameters**:
- `field` (str): The field to validate.
- `value` (Any): The value of the field.
- `form` (Form): The form containing the field.
- `annotation` (list[str], optional): Annotations for the field.
- `strict` (bool): Whether to enforce strict validation.
- `use_annotation` (bool): Whether to use annotations for validation.
- `*args`: Additional arguments.
- `**kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The validated value.

**Raises**:
- `FieldError`: If validation fails.

**Description**:
Validates a specific field in a form, using the active rules.

#### `validate_report`

**Signature**:
```python
async def validate_report(
    self, report: Report, forms: List[Form], strict: bool = True
) -> Report
```

**Parameters**:
- `report` (Report): The report to validate.
- `forms` (List[Form]): A list of forms to include in the report.
- `strict` (bool): Whether to enforce strict validation.

**Returns**:
- `Report`: The validated report.

**Description**:
Validates a report based on active rules.

#### `validate_response`

**Signature**:
```python
async def validate_response(
    self,
    form: Form,
    response: Union[dict, str],
    strict: bool = True,
    use_annotation: bool = True,
) -> Form
```

**Parameters**:
- `form` (Form): The form to validate against.
- `response` (dict | str): The response to validate.
- `strict` (bool): Whether to enforce strict validation.
- `use_annotation` (bool): Whether to use annotations for validation.

**Returns**:
- `Form`: The validated form.

**Raises**:
- `ValueError`: If the response format is invalid.

**Description**:
Validates a response for a given form, ensuring that the response matches the requested fields and adheres to the validation rules.

#### `add_rule`

**Signature**:
```python
def add_rule(self, rule_name: str, rule: Rule, config: dict = None)
```

**Parameters**:
- `rule_name` (str): The name of the rule.
- `rule` (Rule): The rule object.
- `config` (dict, optional): Configuration for the rule.

**Description**:
Adds a new rule to the validator.

#### `remove_rule`

**Signature**:
```python
def remove_rule(self, rule_name: str)
```

**Parameters**:
- `rule_name` (str): The name of the rule to remove.

**Description**:
Removes an existing rule from the validator.

#### `list_active_rules`

**Signature**:
```python
def list_active_rules(self) -> list
```

**Returns**:
- `list`: A list of active rule names.

**Description**:
Lists all active rules.

#### `enable_rule`

**Signature**:
```python
def enable_rule(self, rule_name: str, enable: bool = True)
```

**Parameters**:
- `rule_name` (str): The name of the rule.
- `enable` (bool): Whether to enable or disable the rule.

**Description**:
Enables a specific rule.

#### `disable_rule`

**Signature**:
```python
def disable_rule(self, rule_name: str)
```

**Parameters**:
- `rule_name` (str): The name of the rule to disable.

**Description**:
Disables a specific rule.

#### `log_validation_attempt`

**Signature**:
```python
def log_validation_attempt(self, form: Form, result: dict)
```

**Parameters**:
- `form` (Form): The form being validated.
- `result` (dict): The result of the validation.

**Description**:
Logs a validation attempt.

#### `log_validation_error`

**Signature**:
```python
def log_validation_error(self, field: str, value: Any, error: str)
```

**Parameters**:
- `field` (str): The field that failed validation.
- `value` (Any): The value of the field.
- `error` (str): The error message.

**Description**:
Logs a validation error.

#### `get_validation_summary`

**Signature**:
```python
def get_validation_summary(self) -> Dict[str, Any]
```

**Returns**:
- `dict`: A summary of validation attempts, errors, and successful attempts.

**Description**:
Provides a summary of validation results.
