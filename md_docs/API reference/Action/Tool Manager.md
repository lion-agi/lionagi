

# ToolManager API Reference

The `ToolManager` class is responsible for handling the registration and invocation of tools that are subclasses of [[Base Nodes#^0c90e6|Tool]]. It maintains a registry of tool instances, allowing for dynamic invocation based on tool name and provided arguments. This class supports both synchronous and asynchronous tool function calls.

## Attributes

- `registry (Dict[str, Tool])`: A dictionary to hold registered tools, keyed by their names.

## Methods

### `name_existed(name: str) -> bool`

Checks if a tool name already exists in the registry.

- **Parameters:**
  - `name (str)`: The name of the tool to check.
- **Returns:** `bool` - True if the name exists, False otherwise.
- **Example:**
  ```python
  exists = tool_manager.name_existed("my_tool")
  ```

### `async invoke(func_call: Tuple[str, Dict[str, Any]]) -> Any`

Invokes a registered tool's function with the given arguments. Supports both coroutine and regular functions.

- **Parameters:**
  - `func_call (Tuple[str, Dict[str, Any]])`: A tuple containing the function name and a dictionary of keyword arguments.
- **Returns:** The result of the function call.
- **Raises:** `ValueError` if the function name is not registered or if there's an error during function invocation.
- **Example:**
  ```python
  result = await tool_manager.invoke(("my_tool_function", {"arg1": "value1"}))
  ```

### `get_function_call(response: Dict) -> Tuple[str, Dict]`

Extracts a function call and arguments from a response dictionary.

- **Parameters:**
  - `response (Dict)`: The response dictionary containing the function call information.
- **Returns:** A tuple containing the function name and a dictionary of arguments.
- **Raises:** `ValueError` if the response does not contain valid function call information.
- **Example:**
  ```python
  func_call = tool_manager.get_function_call(response_dict)
  ```

### `register_tools(tools: List[Tool]) -> None`

Registers multiple tools in the registry.

- **Parameters:**
  - `tools (List[Tool])`: A list of tool instances to register.
- **Example:**
  ```python
  tool_manager.register_tools([tool1, tool2])
  ```

### `to_tool_schema_list() -> List[Dict[str, Any]]`

Generates a list of schemas for all registered tools.

- **Returns:** A list of tool schemas.
- **Example:**
  ```python
  schemas = tool_manager.to_tool_schema_list()
  ```


## Usage Example

```python
from lionagi.core.schema import Tool

# Define a new tool subclassing Tool
class MyTool(Tool):
    pass

# Create an instance of MyTool
my_tool = MyTool()

# Initialize ToolManager and register the tool
tool_manager = ToolManager()
tool_manager.register_tools([my_tool])

# Invoke a function of the registered tool
async def invoke_example():
    result = await tool_manager.invoke(("my_tool_function", {"arg1": "value1"}))
    print(result)

# Extract and use a function call from a response
response = {"action": "function_call", "arguments": '{"arg1": "value1"}'}
func_call = tool_manager.get_function_call(response)
```

This API reference provides a detailed overview of the `ToolManager` class, highlighting its capabilities in managing and invoking tools dynamically.
