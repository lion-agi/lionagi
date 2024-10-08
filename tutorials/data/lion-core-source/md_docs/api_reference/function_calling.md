# FunctionCalling API Documentation

The `FunctionCalling` class represents a specific type of ObservableAction for function calls. It manages function tools and arguments, and handles the invocation of functions within the Lion framework.

## Class: FunctionCalling

Inherits from: `ObservableAction`

### Attributes

- `func_tool: Tool | None` - The tool containing the function to be invoked.
- `arguments: dict[str, Any] | None` - Arguments for the function invocation.
- `function_name: str | None` - Name of the function to be called.

### Methods

#### `__init__(func_tool: Tool, arguments: dict[str, Any], retry_config: dict[str, Any] | None = None)`

Initializes a FunctionCalling instance.

- **Parameters:**
  - `func_tool: Tool` - The tool containing the function to be invoked.
  - `arguments: dict[str, Any]` - Arguments for the function invocation.
  - `retry_config: dict[str, Any] | None` - Configuration for retry attempts (default: None).

#### `async invoke() -> Any`

Asynchronously invokes the function with stored arguments.

- **Returns:**
  - `Any` - Result of the function call, possibly processed.
- **Raises:**
  - `Exception` - If function call or processing steps fail.

#### `__str__() -> str`

Returns a string representation of the function call.

- **Returns:**
  - `str` - String representation of the function call.

#### `__repr__() -> str`

Returns a detailed string representation of the function call.

- **Returns:**
  - `str` - Detailed string representation of the function call.

## Usage Example

```python
from lion_core.action.tool import Tool

# Assume we have a Tool instance
my_tool = Tool(function=lambda x: x * 2, function_name="double")

func_call = FunctionCalling(
    func_tool=my_tool,
    arguments={"x": 5},
    retry_config={"max_retries": 3, "delay": 1}
)

# Invoke the function
result = await func_call.invoke()
print(f"Result: {result}")  # Output: Result: 10

# String representation
print(str(func_call))  # Output: double({"x": 5})
print(repr(func_call))  # Output: FunctionCalling(function=double, arguments={"x": 5})
```

This example demonstrates how to create a FunctionCalling instance, invoke the function, and use its string representations.
