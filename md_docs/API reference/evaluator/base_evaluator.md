
### Class: `BaseEvaluator`

**Description**:
`BaseEvaluator` is a class for evaluating mathematical and boolean expressions from strings using Python's AST. It includes a cache for evaluated expressions and supports a set of predefined operators.

#### Attributes:
- `allowed_operators` (Dict[type, Any]): A dictionary mapping AST node types to their corresponding Python operator functions.
- `cache` (Dict[Tuple[str, Tuple], Any]): A dictionary used to cache the results of evaluated expressions and sub-expressions.

### Method: `evaluate`

**Signature**:
```python
def evaluate(expression: str, context: Dict[str, Any]) -> Any:
```

**Parameters**:
- `expression` (str): The expression to evaluate.
- `context` (Dict[str, Any]): A dictionary mapping variable names to their values.

**Return Values**:
- `Any`: The result of the evaluated expression.

**Exceptions Raised**:
- `ValueError`: If the expression cannot be evaluated.

**Description**:
Evaluates a given expression string using the provided context.

**Usage Examples**:
```python
context = {'x': 10, 'y': 20}
expression = 'x + y'
result = evaluator.evaluate(expression, context)
print(result)  # Output: 30
```

### Method: `add_custom_operator`

**Signature**:
```python
def add_custom_operator(operator_name: str, operation_func: Callable) -> None:
```

**Parameters**:
- `operator_name` (str): The name of the custom operator.
- `operation_func` (Callable): The function implementing the custom operator.

**Return Values**:
- `None`

**Exceptions Raised**:
- `ValueError`: If the custom operator is already defined.

**Description**:
Adds a custom operator to the evaluator.

**Usage Examples**:
```python
def custom_add(x, y):
    return x + y + 1

evaluator.add_custom_operator('CustomAdd', custom_add)
```

### Method: `evaluate_file`

**Signature**:
```python
def evaluate_file(file_path: str, context: Dict[str, Any], format: str = "line") -> Any:
```

**Parameters**:
- `file_path` (str): The path to the file containing expressions.
- `context` (Dict[str, Any]): A dictionary mapping variable names to their values.
- `format` (str, optional): The format of the file, either "line" or "json". Default is "line".

**Return Values**:
- `Any`: The result of the last evaluated expression.

**Exceptions Raised**:
- `ValueError`: If the file format is unsupported.

**Description**:
Evaluates expressions from a file.

**Usage Examples**:
```python
result = evaluator.evaluate_file('expressions.txt', context)
print(result)
```

### Method: `validate_expression`

**Signature**:
```python
def validate_expression(expression: str) -> Tuple[bool, str]:
```

**Parameters**:
- `expression` (str): The expression to validate.

**Return Values**:
- `Tuple[bool, str]`: A tuple containing a boolean indicating if the expression is valid, and a message.

**Description**:
Validates the given expression.

**Usage Examples**:
```python
is_valid, message = evaluator.validate_expression('x + y')
print(is_valid, message)  # Output: True, "Expression is valid."
```

### Class: `BaseEvaluationEngine`

**Description**:
`BaseEvaluationEngine` is a class for executing scripts that involve variable assignments and function calls. It provides basic functionalities to evaluate expressions, assign variables, and execute predefined functions.

#### Attributes:
- `variables` (Dict[str, Any]): A dictionary of variables used in the script.
- `functions` (Dict[str, Callable]): A dictionary of functions that can be called in the script.

### Method: `_evaluate_expression`

**Signature**:
```python
def _evaluate_expression(self, expression: str) -> Any:
```

**Parameters**:
- `expression` (str): The expression to evaluate.

**Return Values**:
- `Any`: The result of the evaluated expression.

**Exceptions Raised**:
- `ValueError`: If a variable is undefined.

**Description**:
Evaluates an expression within the script's context.

**Usage Examples**:
```python
engine.variables = {'x': 10}
result = engine._evaluate_expression('x * 2')
print(result)  # Output: 20
```

### Method: `_assign_variable`

**Signature**:
```python
def _assign_variable(self, var_name: str, value: Any) -> None:
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
engine._assign_variable('y', 5)
print(engine.variables)  # Output: {'y': 5}
```

### Method: `_execute_function`

**Signature**:
```python
def _execute_function(self, func_name: str, *args: Any) -> None:
```

**Parameters**:
- `func_name` (str): The name of the function to execute.
- `*args` (Any): The arguments to pass to the function.

**Return Values**:
- `None`

**Exceptions Raised**:
- `ValueError`: If the function is not defined.

**Description**:
Executes a predefined function with the given arguments.

**Usage Examples**:
```python
engine.functions = {'print': print}
engine._execute_function('print', 'Hello, World!')
# Output: Hello, World!
```

### Method: `_execute_statement`

**Signature**:
```python
def _execute_statement(self, stmt: ast.AST) -> None:
```

**Parameters**:
- `stmt` (ast.AST): The AST statement node to execute.

**Return Values**:
- `None`

**Exceptions Raised**:
- `ValueError`: If an unsupported statement type is encountered.

**Description**:
Executes a single statement from the script.

**Usage Examples**:
```python
stmt = ast.parse('x = 10').body[0]
engine._execute_statement(stmt)
print(engine.variables)  # Output: {'x': 10}
```

### Method: `execute`

**Signature**:
```python
def execute(self, script: str) -> None:
```

**Parameters**:
- `script` (str): The script to execute.

**Return Values**:
- `None`

**Description**:
Parses and executes a script, handling variable assignments and function calls.

**Usage Examples**:
```python
script = """
x = 10
y = x * 2
print(y)
"""
engine.execute(script)
# Output: 20
```
