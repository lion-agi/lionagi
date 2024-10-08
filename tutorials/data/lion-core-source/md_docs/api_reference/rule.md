# Rule API Documentation

## Overview

The `Rule` class is an abstract base class in the Lion framework for defining and enforcing rules on data. It provides a structure for creating rules that can be applied to specific fields and values.

## Class Definition

```python
class Rule(Element):
    """Base class for defining rules in the Lion framework."""
```

## Attributes

- `info: Note` - A Note object containing additional information or configuration for the rule.
- `validation_kwargs: dict` - A dictionary of keyword arguments used during validation.

## Constructor

```python
def __init__(self, info: Note = None, **kwargs):
```

Initialize a Rule instance with optional additional information and keyword arguments.

## Methods

### Rule Application

#### `apply`

```python
async def apply(self, field: str, value: Any, annotation=None, check_func: Callable = None, **kwargs) -> bool:
```

Determine if the rule should be applied to a given field and value.

#### `validate`

```python
async def validate(self, value) -> Any:
```

Validate a value against the rule. This method should be implemented by subclasses.

### Rule Checking

#### `check_value`

```python
async def check_value(self, value, /) -> Any:
```

Check if a value is valid according to the rule. This method should be implemented by subclasses.

#### `fix_value`

```python
async def fix_value(self, value) -> Any:
```

Attempt to fix an invalid value. This method should be implemented by subclasses.

## Usage Examples

Since `Rule` is an abstract base class, it's typically subclassed to create specific rules. Here's an example of how a subclass might be implemented and used:

```python
class StringLengthRule(Rule):
    def __init__(self, min_length: int, max_length: int, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length

    async def check_value(self, value, /) -> bool:
        return self.min_length <= len(value) <= self.max_length

    async def fix_value(self, value) -> str:
        if len(value) < self.min_length:
            return value.ljust(self.min_length)
        if len(value) > self.max_length:
            return value[:self.max_length]
        return value

# Using the rule
string_rule = StringLengthRule(min_length=5, max_length=10)

async def validate_string(value: str):
    if await string_rule.apply("some_field", value):
        try:
            return await string_rule.validate(value)
        except ValueError:
            return await string_rule.fix_value(value)
    return value
```

## Best Practices

1. Always implement the `check_value` and `fix_value` methods in subclasses of `Rule`.
2. Use the `info` attribute to store additional configuration or metadata about the rule.
3. Make use of the `apply` method to determine if a rule should be applied to a specific field or value.
4. When implementing complex rules, consider breaking them down into smaller, composable rules.
5. Use type hints in your rule implementations to improve code readability and catch potential type errors early.
6. Leverage the `validation_kwargs` attribute for passing additional parameters to validation methods.

## Notes

- The `Rule` class is designed to be subclassed. Direct instances of `Rule` are not meant to be used.
- The `apply` method determines if a rule should be applied, while `validate` performs the actual validation.
- The `check_value` method should return a boolean indicating if the value is valid, while `fix_value` should attempt to correct invalid values.
- Rules can be combined and used in conjunction with other components in the Lion framework, such as the `RuleBook` and `RuleProcessor`.
