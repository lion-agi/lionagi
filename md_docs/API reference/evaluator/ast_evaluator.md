
### Class: `ASTEvaluator`

**Description**:
`ASTEvaluator` safely evaluates expressions using Abstract Syntax Tree (AST) parsing to prevent unsafe operations.

### Method: `evaluate`

**Signature**:
```python
def evaluate(expression: str, context: dict) -> bool:
```

**Parameters**:
- `expression` (str): The condition expression to evaluate.
- `context` (dict): The context in which to evaluate the expression, providing values for variables.

**Return Values**:
- `bool`: The result of the evaluated expression.

**Exceptions Raised**:
- `ValueError`: If the expression evaluation fails.

**Description**:
Evaluates a condition expression within a given context using AST parsing.

**Usage Examples**:
```python
context = {'x': 10, 'y': 20}
expression = 'x < y'
result = evaluator.evaluate(expression, context)
print(result)  # Output: True
```

### Class: `ASTEvaluationEngine`

**Description**:
`ASTEvaluationEngine` executes scripts safely using the `ASTEvaluator` for expression evaluation, managing variable assignments and function calls.

### Method: `process_data`

**Signature**:
```python
def process_data(data: Any) -> Any:
```

**Parameters**:
- `data` (Any): The data to process.

**Return Values**:
- `Any`: The processed data.

**Description**:
Processes the given data (e.g., doubles the input).

**Usage Examples**:
```python
result = engine.process_data(5)
print(result)  # Output: 10
```

### Method: `_evaluate_expression`

**Signature**:
```python
def _evaluate_expression(expression: str) -> Any:
```

**Parameters**:
- `expression` (str): The expression to evaluate.

**Return Values**:
- `Any`: The evaluated result of the expression.

**Description**:
Evaluates expressions within scripts using `ASTEvaluator`.

**Usage Examples**:
```python
engine.variables = {'x': 5}
result = engine._evaluate_expression('x + 10')
print(result)  # Output: 15
```

### Method: `_assign_variable`

**Signature**:
```python
def _assign_variable(var_name: str, value: Any) -> None:
```

**Parameters**:
- `var_name` (str): The name of the variable.
- `value` (Any): The value to assign to the variable.

**Return Values**:
- `None`

**Description**:
Assigns a value to a variable within the script's context.

**Usage Examples**:
```python
engine._assign_variable('x', 5)
print(engine.variables)  # Output: {'x': 5}
```

### Method: `_execute_function`

**Signature**:
```python
def _execute_function(func_name: str, arg: Any) -> Any:
```

**Parameters**:
- `func_name` (str): The name of the function to execute.
- `arg` (Any): The argument to pass to the function.

**Return Values**:
- `Any`: The result of the function execution.

**Exceptions Raised**:
- `ValueError`: If the function is not defined.

**Description**:
Executes a predefined function with the given argument.

**Usage Examples**:
```python
engine.functions = {'process_data': engine.process_data}
result = engine._execute_function('process_data', 5)
print(result)  # Output: 10
```

### Method: `execute`

**Signature**:
```python
def execute(script: str) -> None:
```

**Parameters**:
- `script` (str): The script to execute.

**Return Values**:
- `None`

**Exceptions Raised**:
- `ValueError`: If an unsupported statement type is encountered in script execution.

**Description**:
Parses and executes a script, handling variable assignments and function calls.

**Usage Examples**:
```python
script = """
x = 10
y = process_data(x)
"""
engine.execute(script)
print(engine.variables)  # Output: {'x': 10, 'y': 20}
```
