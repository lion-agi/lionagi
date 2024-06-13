
## Class: `DirectiveTemplate`

**Description**:
`DirectiveTemplate` is an enhanced template processing class that supports conditionals and loops within template strings. It provides methods for rendering templates with dynamic content based on the provided context.

**Attributes**:
- `template_str (str)`: The template string to be processed.
- `evaluator (BaseEvaluator)`: An evaluator instance to evaluate conditional expressions.

**Usage Examples**:
```python
template_str = """
{if condition}Condition is true{else}Condition is false{endif}
{for item in items}{item} {endfor}
"""

context = {
    "condition": True,
    "items": [1, 2, 3]
}

template = DirectiveTemplate(template_str)
output = template.fill(context=context)
print(output)
# Output:
# Condition is true
# 1 2 3 
```

### `__init__`

**Signature**:
```python
def __init__(self, template_str: str)
```

**Parameters**:
- `template_str (str)`: The template string to be processed.

**Description**:
Initializes a new instance of the `DirectiveTemplate` class with the provided template string.

**Usage Examples**:
```python
template = DirectiveTemplate("Hello, {name}!")
```

### `_render_conditionals`

**Signature**:
```python
def _render_conditionals(self, context: Dict[str, Any]) -> str
```

**Parameters**:
- `context (Dict[str, Any])`: The context dictionary containing values to evaluate the conditionals.

**Return Values**:
- `str`: The template string with conditionals processed.

**Description**:
Processes conditional statements in the template string. Supports `{if}`, `{else}`, and `{endif}` statements.

**Usage Examples**:
```python
template_str = "{if condition}True{else}False{endif}"
context = {"condition": True}
output = template._render_conditionals(context)
print(output)
# Output: True
```

### `_render_loops`

**Signature**:
```python
def _render_loops(self, template: str, context: Dict[str, Any]) -> str
```

**Parameters**:
- `template (str)`: The template string to be processed.
- `context (Dict[str, Any])`: The context dictionary containing values for loop iteration.

**Return Values**:
- `str`: The template string with loops processed.

**Description**:
Processes loop statements in the template string. Supports `{for}` and `{endfor}` statements.

**Usage Examples**:
```python
template_str = "{for item in items}{item} {endfor}"
context = {"items": [1, 2, 3]}
output = template._render_loops(template_str, context)
print(output)
# Output: 1 2 3 
```

### `fill`

**Signature**:
```python
def fill(self, template_str: str = "", context: Dict[str, Any] = {}) -> str
```

**Parameters**:
- `template_str (str, optional)`: The template string to be processed. Defaults to the instance's template string.
- `context (Dict[str, Any], optional)`: The context dictionary containing values to fill the template. Defaults to an empty dictionary.

**Return Values**:
- `str`: The filled template string with all placeholders, conditionals, and loops processed.

**Description**:
Fills the template with values from the context after processing conditionals and loops.

**Usage Examples**:
```python
template_str = """
{if condition}Condition is true{else}Condition is false{endif}
{for item in items}{item} {endfor}
"""

context = {
    "condition": True,
    "items": [1, 2, 3]
}

template = DirectiveTemplate(template_str)
output = template.fill(context=context)
print(output)
# Output:
# Condition is true
# 1 2 3 
```
