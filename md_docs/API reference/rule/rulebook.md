
### Class: `RuleBook`

**Description**:
`RuleBook` manages a collection of rules, providing methods to access and apply rules. It maintains logs of applied and invoked rules, and allows configuration of rules through a dictionary.

#### Attributes:
- `rules` (dict[str, Rule] | list[Rule] | None): A dictionary or list of rules to be managed by the rulebook.
- `ruleorder` (list[str] | None): A list specifying the order in which rules should be applied.
- `rule_config` (dict[str, dict] | None): A dictionary containing configuration for each rule.

### Method: `__init__`

**Signature**:
```python
def __init__(
    self,
    rules: dict[str, Rule] | list[Rule] = None,
    ruleorder: list[str] = None,
    rule_config: dict[str, dict] = None,
)
```

**Parameters**:
- `rules` (dict[str, Rule] | list[Rule] | None): A dictionary or list of rules to be managed by the rulebook. Default is `None`.
- `ruleorder` (list[str] | None): A list specifying the order in which rules should be applied. Default is `None`.
- `rule_config` (dict[str, dict] | None): A dictionary containing configuration for each rule. Default is `None`.

**Description**:
Initializes the `RuleBook` with the specified rules, rule order, and rule configuration.

### Property: `_all_applied_log`

**Signature**:
```python
@property
def _all_applied_log(self):
```

**Return Values**:
- `list`: A list of all applied logs from all rules in the rulebook.

**Description**:
Returns all applied logs from all rules in the rulebook.

### Property: `_all_invoked_log`

**Signature**:
```python
@property
def _all_invoked_log(self):
```

**Return Values**:
- `list`: A list of all invoked logs from all rules in the rulebook.

**Description**:
Returns all invoked logs from all rules in the rulebook.

### Method: `__getitem__`

**Signature**:
```python
def __getitem__(self, key: str) -> Rule:
```

**Parameters**:
- `key` (str): The key of the rule to retrieve.

**Return Values**:
- `Rule`: The rule associated with the given key.

**Description**:
Retrieves a rule from the rulebook by its key.

**Usage Examples**:
```python
# Example 1: Initializing a RuleBook with rules and rule order
rules = {
    "boolean_rule": BooleanRule(),
    "number_rule": NumberRule(validation_kwargs={"upper_bound": 100}),
}
rulebook = RuleBook(rules=rules, ruleorder=["boolean_rule", "number_rule"])

# Example 2: Accessing a rule by its key
boolean_rule = rulebook["boolean_rule"]

# Example 3: Getting all applied logs
applied_logs = rulebook._all_applied_log
print(applied_logs)

# Example 4: Getting all invoked logs
invoked_logs = rulebook._all_invoked_log
print(invoked_logs)
```
