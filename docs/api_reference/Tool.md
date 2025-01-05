---
type: api-reference
title: "LionAGI Tool API Reference"
created: 2025-01-05 03:41 EST
updated: 2025-01-05 03:41 EST
status: active
tags: [api-reference, lionagi, operatives, action, tool]
aliases: ["Tool API"]
sources: 
  - "Local: /users/lion/lionagi/lionagi/operatives/action/tool.py"
confidence: certain
---

# Tool API Reference

## Overview

The Tool class provides a robust system for wrapping callable objects with schema validation and processing capabilities. Built on [[Element|Element]], it enables function inspection, parameter validation, and pre/post processing hooks.

Used by [[Function Calling|FunctionCalling]] for executing functions and by [[Action Manager|ActionManager]] for managing tool collections.

Key features:
- Function wrapping
- Schema validation
- Processing hooks
- Parameter inspection

## Core Components

### Tool Class

```python
class Tool(Element):
    """Function wrapper with schema validation and processing.
    
    Wraps callable objects with validation and processing hooks.
    Used by FunctionCalling for execution control.
    """
    
    # Core function
    func_callable: Callable[..., Any] = Field(
        ...,  # Required
        description="Function to wrap",
        exclude=True,
    )
    
    # Schema handling
    tool_schema: dict[str, Any] | None = Field(
        default=None,
        description="Function parameter schema"
    )
    
    # Processing hooks
    preprocessor: Callable[[Any], Any] | None = Field(
        default=None,
        description="Input preprocessor",
        exclude=True,
    )
    preprocessor_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Preprocessor arguments",
        exclude=True,
    )
    postprocessor: Callable[[Any], Any] | None = Field(
        default=None,
        description="Output postprocessor",
        exclude=True,
    )
    postprocessor_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Postprocessor arguments",
        exclude=True,
    )
    
    # Validation control
    strict_func_call: bool = Field(
        default=False,
        description="Strict parameter validation"
    )
```

Integration points:
- Inherits from [[Element|Element]]
- Used by [[Function Calling|FunctionCalling]]
- Managed by [[Action Manager|ActionManager]]

## Validation System

### _validate_func_callable()
```python
@field_validator("func_callable", mode="before")
def _validate_func_callable(cls, value: Any) -> Callable[..., Any]:
    """Validate function is callable.
    
    Uses common_field_validators.validate_callable for checking.
    """
    return validate_callable(
        cls, value, undefind_able=False, check_name=True
    )
```

### _validate_tool_schema()
```python
@model_validator(mode="after")
def _validate_tool_schema(self) -> Self:
    """Generate schema if not provided.
    
    Uses function_to_schema to extract parameter info.
    """
    if self.tool_schema is None:
        self.tool_schema = function_to_schema(self.func_callable)
    return self
```

## Property Methods

### function
```python
@property
def function(self) -> str:
    """Get function name from schema.
    
    Returns:
        str: Function name
    """
    return self.tool_schema["function"]["name"]
```

### required_fields
```python
@property
def required_fields(self) -> set[str]:
    """Get required parameters from schema.
    
    Returns:
        set[str]: Required parameter names
    """
    return set(self.tool_schema["function"]["parameters"]["required"])
```

### minimum_acceptable_fields
```python
@property
def minimum_acceptable_fields(self) -> set[str]:
    """Get minimum required parameters from signature.
    
    Uses inspect.signature to find non-default parameters.
    Excludes *args and **kwargs.
    
    Returns:
        set[str]: Minimum required parameter names
    """
    try:
        a = {
            k
            for k, v in inspect.signature(
                self.func_callable
            ).parameters.items()
            if v.default == inspect.Parameter.empty
        }
        if "kwargs" in a:
            a.remove("kwargs")
        if "args" in a:
            a.remove("args")
        return a
    except Exception:
        return set()
```

## Type Aliases

### Function Tools
```python
# Direct function tools
FuncTool: TypeAlias = Tool | Callable[..., Any]

# Function references
FuncToolRef: TypeAlias = FuncTool | str

# Tool references
ToolRef: TypeAlias = FuncToolRef | list[FuncToolRef] | bool
```

Used for:
- Direct function wrapping (FuncTool)
- Function referencing (FuncToolRef)
- Tool collection handling (ToolRef)

## Implementation Notes

1. Function Wrapping
   - Callable validation
   - Schema generation
   - Parameter inspection
   - Name tracking

2. Schema Handling
   - Automatic generation
   - Parameter validation
   - Required fields
   - Minimum fields

3. Processing Hooks
   - Input preprocessing
   - Output postprocessing
   - Argument passing
   - Hook validation

4. Performance
   - Lazy schema generation
   - Efficient validation
   - Minimal overhead
   - Quick inspection

## Usage Examples

### Basic Tool
```python
# Create basic tool
def my_function(arg1: str, arg2: int = 0) -> str:
    return f"{arg1} {arg2}"

tool = Tool(
    func_callable=my_function,
    strict_func_call=True
)
```

### With Processing
```python
# Add processing hooks
def preprocess(args: dict) -> dict:
    args["arg1"] = args["arg1"].upper()
    return args

def postprocess(result: str) -> str:
    return f"Result: {result}"

tool = Tool(
    func_callable=my_function,
    preprocessor=preprocess,
    postprocessor=postprocess
)
```

### Schema Validation
```python
# Validate parameters
tool = Tool(
    func_callable=my_function,
    strict_func_call=True
)

# Check required fields
required = tool.required_fields  # {"arg1"}
minimum = tool.minimum_acceptable_fields  # {"arg1"}
```

## Protocol Relationships

### Core Integration
- [[Element]] - Base element
- [[Function Calling]] - Function execution
- [[Action Manager]] - Tool management

### Action System
- [[Action System MOC]] - System overview
- [[Action Request Message]] - Request handling
- [[Action Response Message]] - Response handling

### Cross-System
- [[Validation API Reference]] - Schema validation
- [[Processor API Reference]] - Processing hooks
- [[Schema API Reference]] - Schema handling

## Implementation References
- [[Element]] - Element base
- [[Function Calling]] - Execution
- [[Action Manager]] - Management
