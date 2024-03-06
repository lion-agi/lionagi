---
tags:
  - Core
  - LLM
  - API
  - Session
created: 2024-02-26
completed: true
---


# Branch Class API Reference

> Child class of [[BaseBranch]]


## Overview

The `Branch` class extends the `BaseBranch` class within the `lionagi` system, incorporating additional functionalities for tool management, service integration, and advanced message handling specific to a conversation branch.

## Class Definition

```python
class Branch(BaseBranch):
```

### Inherits From
- `BaseBranch`: Inherits functionalities related to managing branches of conversation.

## Constructor

```python
def __init__(self, branch_name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, instruction_sets=None, tool_manager=None, **kwargs):
```

Initializes a new instance of the `Branch` class with enhanced features for conversation management.

### Parameters

- `branch_name`: Optional name for the branch.
- `system`: System message or configuration.
- `messages`: Initial set of messages as a `pandas.DataFrame`.
- [[API Utilities#^4350a9|service]]: External service integration, e.g., OpenAI.
- `sender`: Default sender identifier for messages. ^fc105b
- `llmconfig`: Configuration for language models or external APIs.
- [[Base Component#^0c90e6|tools]]: Collection of tools to be registered with the branch.
- `datalogger`: A `DataLogger` instance for logging branch operations.
- `persist_path`: Filesystem path for data persistence.
- `instruction_sets`: Sets of instructions for managing conversation flows.
- [[Tool Manager]]: An instance of `ToolManager` for managing tools within the branch.
- `**kwargs`: Additional keyword arguments passed to the base class constructor.

## Factory Methods

### from_csv

```python
@classmethod
def from_csv(cls, filepath, branch_name=None, service=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, instruction_sets=None, tool_manager=None, read_kwargs=None, **kwargs):
```

Creates an instance of `Branch` from a CSV file, loading messages and configurations.

### from_json

```python
@classmethod
def from_json(cls, filepath, branch_name=None, service=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, instruction_sets=None, tool_manager=None, read_kwargs=None, **kwargs):
```

Creates an instance of `Branch` from a JSON file, loading messages and configurations.

## Instance Methods

### messages_describe

```python
def messages_describe(self) -> Dict[str, Any]:
```

Provides a detailed summary of the branch, including messages, tools, and instruction sets.

### has_tools

```python
@property
def has_tools(self) -> bool:
```

Indicates whether the branch has any registered tools.


### merge_branch

```python
def merge_branch(self, branch: "Branch", update: bool = True) -> None:
```

Merges another branch into this one, combining messages, datalogger contents, and optionally instruction sets and tools.

### register_tools

```python
def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
```

Registers a tool or a list of tools with the branch.

### delete_tools

```python
def delete_tools(self, tools: Union[bool, T, List[T], str, List[str], List[Dict[str, Any]]], verbose: bool = True) -> bool:
```

Deletes specified tools from the branch's tool manager.

### send

```python
def send(self, recipient: str, category: str, package: Any) -> None:
```

Sends a package to a recipient within the branch, categorizing the package for specific handling.

### receive

```python
def receive(self, sender: str, messages: bool = True, tools: bool = True, service: bool = True, llmconfig: bool = True) -> None:
```

Receives and processes packages sent by a sender, integrating the content into the branch as specified.

### receive_all

```python
def receive_all(self) -> None:
```

Processes all pending packages sent to the branch.

### add_message (Overridden)

```python
def add_message(self, system: Optional[Union[dict, list, System]] = None, instruction: Optional[Union[dict, list, Instruction]] = None, context: Optional[Union[str, Dict[str, Any]]] = None, response: Optional[Union[dict, list, Response]] = None, sender: Optional[str] = None) -> None:
```

Adds a message to the branch, extending `BaseBranch`'s method with additional functionalities.

## ChatFlow Methods

> Uses [[MonoFlow]], to conduct interactions with [LLM](https://en.wikipedia.org/wiki/Large_language_model)

#### call_chatcompletion

^c7d696

```python
async def call_chatcompletion(self, sender=None, with_sender=False, **kwargs):
```

Asynchronously invokes chat completion actions within the branch.

#### chat

```python
async def chat(self, instruction: Union[Instruction, str], context: Optional[Any] = None, sender: Optional[str] = None, system: Optional[Union[System, str, Dict[str, Any]]] = None, tools: Union[bool, T, List[T], str, List[str]] = False, out: bool = True, invoke: bool = True, **kwargs) -> Any:
```

Conducts an asynchronous chat flow within the branch based on the given instruction and context.

#### ReAct

```python
async def ReAct(self, instruction: Union[Instruction, str], context=None, sender=None, system=None, tools=None, num_rounds: int = 1, **kwargs):
```

Performs an asynchronous reaction to an instruction, potentially involving multiple rounds of conversation.

#### auto_followup

```python
async def auto_followup(self, instruction: Union[Instruction, str], context=None, sender=None, system=None, tools: Union[bool, T, List[T], str, List[str], List[Dict]] = False, max_followup: int = 3, out=True, **kwargs) -> None:
```

Automatically follows up on a conversation flow asynchronously, respecting a maximum number of follow-ups.
