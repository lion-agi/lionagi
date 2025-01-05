# lionagi.action

```
Function execution system providing validation and tracking.

This module handles:
- Function registration and execution through ActionManager
- Function wrapping with Tool
- Execution state tracking with FunctionCalling

Example:
    >>> from lionagi.action import ActionManager
    >>> def add(x: int, y: int) -> int:
    ...     return x + y
    ...
    >>> manager = ActionManager()
    >>> manager.register_tool(add)
    >>> result = await manager.invoke({
    ...     "function": "add",
    ...     "arguments": {"x": 1, "y": 2}
    ... })
    >>> result.execution.response
    3
```

## ActionManager

Central registry for managing function tools.

```python
class ActionManager:
    """Function tool registry and execution manager.

    Example:
        >>> manager = ActionManager()
        >>> manager.register_tool(add)
        >>> result = await manager.invoke({
        ...     "function": "add",
        ...     "arguments": {"x": 1, "y": 2}
        ... })
    """
```

### Methods

#### register_tool(tool, *, update=False)
Register a function or Tool object.

Parameters:
- **tool** (*Callable | Tool*) - Function/Tool to register
- **update** (*bool*) - Allow updating existing tools

Raises:
- TypeError - Invalid tool type
- ValueError - Tool exists and update=False

Example:
```python
>>> def multiply(x: int, y: int) -> int:
...     return x * y
...
>>> manager.register_tool(multiply)
```

#### register_tools(tools, *, update=False) 
Register multiple functions/tools.

Parameters:
- **tools** (*list[Callable | Tool]*) - Items to register
- **update** (*bool*) - Allow updates

Example:
```python
>>> manager.register_tools([add, multiply])
```

#### async invoke(func_call)
Execute a registered function.

Parameters:
- **func_call** (*dict | ActionRequest*) - Function specification

Returns:
- FunctionCalling - Contains execution results

Raises:
- ValueError - Unknown function/invalid args
- RuntimeError - Execution failed

Example:
```python
>>> result = await manager.invoke({
...     "function": "add",
...     "arguments": {"x": 1, "y": 2}
... })
>>> result.execution.response
3
```

## Tool

Function wrapper with validation.

```python
class Tool:
    """Function wrapper with validation.

    Example:
        >>> def validate(args):
        ...     if args["x"] <= 0:
        ...         raise ValueError("x must be positive")
        ...     return args
        ...
        >>> tool = Tool(add, pre_processor=validate)
    """
```

### Methods

#### __init__(function, *, pre_processor=None, post_processor=None)
Initialize function wrapper.

Parameters:
- **function** (*Callable*) - Function to wrap
- **pre_processor** (*Callable, optional*) - Input validation
- **post_processor** (*Callable, optional*) - Output processing

Example:
```python
>>> def validate(args):
...     if args["x"] <= 0:
...         raise ValueError("x must be positive")
...     return args
...
>>> tool = Tool(add, pre_processor=validate)
```

## FunctionCalling

Execution state tracker.

```python
class FunctionCalling:
    """Track function execution state.

    Example:
        >>> caller = FunctionCalling(tool, arguments={"x": 1, "y": 2})
        >>> await caller.invoke()
        >>> caller.execution.status
        'completed'
    """
```

### Attributes

#### status
Current execution state.

Type:
- EventStatus

Values:
- PENDING - Initial state
- PROCESSING - During execution
- COMPLETED - Success
- FAILED - Error occurred

#### execution_time
Execution duration in seconds.

Type:
- float | None

#### execution_response
Function result if successful.

Type:
- Any

#### execution_error
Error message if failed.

Type:
- str | None

### Methods

#### async invoke()
Execute the function.

Example:
```python
>>> caller = FunctionCalling(tool, arguments={"x": 1, "y": 2})
>>> await caller.invoke()
>>> print(caller.execution.status)
'completed'
```

## Error Handling

Basic error handling patterns:

```python
# Handle validation error
try:
    result = await manager.invoke({
        "function": "add",
        "arguments": {"x": "not a number", "y": 2}
    })
except ValueError as e:
    print(f"Invalid arguments: {e}")

# Handle execution error    
try:
    result = await manager.invoke(func_call)
except RuntimeError as e:
    print(f"Execution failed: {e}")
    print(f"Status: {result.execution.status}")
```
