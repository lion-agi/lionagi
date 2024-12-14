# LionAGI Action API Reference

This document provides a comprehensive reference for the classes and their APIs defined within the `action` module. These classes manage the lifecycle of actions, including creation, execution, logging, and tool invocation.

## Table of Contents
- [Overview](#overview)
- [Core Classes](#core-classes)
  - [Action](#action)
  - [ActionExecutor](#actionexecutor)
  - [FunctionCalling](#functioncalling)
  - [ActionManager](#actionmanager)
  - [ActionProcessor](#actionprocessor)
  - [Tool](#tool)
  - [FuncTool](#functool)

## Overview

The `action` module provides a set of classes and utilities to define, manage, and execute asynchronous actions. Core concepts include:

- **Action**: A base unit of work with associated status, results, and logging
- **FunctionCalling**: A specialized `Action` for invoking asynchronous tools
- **ActionExecutor**: Coordinates and processes a queue of actions
- **ActionManager**: Manages a registry of tools and provides interfaces for registration/invocation
- **ActionProcessor**: Handles the asynchronous processing lifecycle
- **Tool**: Wraps callable functions with schema validation and metadata
- **FuncTool**: A type alias for `Tool` or async callable function

## Core Classes

### Action
**Location:** `lionagi/action/base.py`

#### Description
Represents an executable action with status tracking, timing, results, and error handling capabilities. Serves as a base class for more specialized actions.

#### Attributes
- `status` (`EventStatus`): Current status of the action (default: `EventStatus.PENDING`)
- `execution_time` (`float | None`): Execution duration in seconds
- `execution_result` (`Any | None`): Result upon completion
- `error` (`str | None`): Error message if failure occurs
- `created_at` (`datetime`): Creation timestamp (auto-populated with `datetime.utcnow()`)

#### Methods
- `to_log() -> Log`: Converts action to a `Log` object for auditing
- `from_dict(...) -> NoReturn`: Raises `NotImplementedError`
- `request` (property): Returns request payload dictionary

#### Example
```python
from lionagi.action import Action, EventStatus

action = Action()
print(action.status)           # PENDING
print(action.execution_time)   # None
print(action.to_log())        # Returns a Log instance
```

### ActionExecutor
**Location:** `lioncore/action/action_executor.py`

#### Description
Executes and manages asynchronous actions using a queue system. Ensures ordered processing, tracks completion, and interfaces with `ActionProcessor`.

#### Attributes
- `processor_class` (`type[ActionProcessor]`): Processor class for queued actions
- `strict` (`bool`): Enforces type checking for action pile
- `pile` (`Pile[Action]`): Internal collection of actions
- `pending` (`Progression`): Tracks pending actions
- `processor` (`ActionProcessor | None`): Active processor instance

#### Properties
- `pending_action` (`Pile[Action]`): Actions with `EventStatus.PENDING`
- `completed_action` (`Pile[Action]`): Actions with `EventStatus.COMPLETED`

#### Methods
- `__init__(*kwargs)`: Initialize with optional processor config
- `append(action: Action) -> None` (async): Add new action to pile
- `forward() -> None` (async): Process all pending actions

#### Example
```python
import asyncio
from lionagi.action import ActionExecutor, Action

executor = ActionExecutor()
async def run_actions():
    await executor.append(Action())
    await executor.forward()

asyncio.run(run_actions())
```

### FunctionCalling
**Location:** `lionagi/action/function_calling.py`

#### Description
Specialized Action for asynchronous tool invocation with execution tracking and error handling.

#### Attributes
- `arguments` (`dict[str, Any]`): Tool function arguments
- `tool_id` (`IDType | None`): Tool identifier post-validation

#### Methods
- `invoke() -> None` (async): Executes tool function with timing and error handling

#### Example
```python
import asyncio
from lionagi.action import FunctionCalling, Tool

async def async_func(param: str) -> str:
    return f"Processed: {param}"

tool = Tool(function=async_func)
action = FunctionCalling(_tool=tool, arguments={"param": "data"})

async def run():
    await action.invoke()
    print(action.execution_result)  # "Processed: data"

asyncio.run(run())
```

### ActionManager
**Location:** `lionagi/action/manager.py`

#### Description
Manages tool registry with registration, validation, and invocation capabilities.

#### Attributes
- `registry` (`dict[ToolName, Tool]`): Validated tool registry

#### Methods
- `__init__(registry: ToolRegistry = {})`: Initialize with optional registry
- `register_tool(tool: FuncTool, update: bool = False, schema: Schema | None = None) -> None`
- `register_tools(tools: ToolInput, update: bool = False) -> None`
- `invoke(function_name: str, arguments: dict[str, Any]) -> FunctionCalling` (async)
- `schema_list` (property): Returns all tool schemas
- `get_tool_schema(tools: ToolSpecifier = False) -> list[Schema] | None`

#### Example
```python
import asyncio
from lionagi.action import ActionManager, FuncTool

async def greet(name: str) -> str:
    return f"Hello, {name}!"

manager = ActionManager()
manager.register_tool(greet)

async def run():
    action = await manager.invoke("greet", {"name": "Alice"})
    print(action.execution_result)  # "Hello, Alice!"

asyncio.run(run())
```

### ActionProcessor
**Location:** `lionagi/action/processor.py`

#### Description
Handles asynchronous action processing with concurrency control and permission management.

#### Class Variables
- `observation_type`: Specifies processable action type

#### Methods
- `process() -> None` (async): Process queued actions with capacity management

### Tool
**Location:** `lionagi/action/tool.py`

#### Description
Function wrapper with schema validation support.

#### Attributes
- `function` (`Callable | AsyncCallable`): Wrapped function
- `schema_` (`Schema | None`): Parameter/return schema
- `tcall` (`TCallParams | None`): Timing/calling config

#### Properties
- `function_name` (`str`): Wrapped function name

#### Example
```python
from lionagi.action import Tool

async def compute(x: int, y: int) -> int:
    return x + y

tool = Tool(function=compute)
print(tool.function_name)  # "compute"
```

### FuncTool
**Type Alias:** `FuncTool = Tool | Callable[..., Awaitable[Any]]`

#### Description
Represents either a Tool instance or async callable.

#### Example
```python
from lionagi.action import FuncTool, Tool
import asyncio

async def foo() -> str:
    return "bar"

ft: FuncTool = foo  # Direct function
ft_tool: FuncTool = Tool(function=foo)  # Wrapped Tool
```

## Integration Patterns

These components work together in a typical workflow:

1. Register tools with `ActionManager`
2. Create actions (e.g., `FunctionCalling`) and queue in `ActionExecutor`
3. Process with `ActionExecutor.forward()` using `ActionProcessor`

This architecture ensures:
- Flexible async operations
- Robust error handling
- Extensible design
- Clear separation of concerns
