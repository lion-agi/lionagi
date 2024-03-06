---
tags:
  - Session
  - Core
  - "#LLM"
  - BaseObj
created: 2024-02-26
completed: true
---

# BaseBranch Class  API Reference

> Child class of [[Base Component#^614ddc|BaseRelatableNode]], `abc.ABC`


## Overview

The `BaseBranch` class serves as the foundational component for managing branches of conversation within the `lionagi` system. It incorporates messages and logging functionality to facilitate detailed conversation tracking and analysis.

## Class Definition

```python
class BaseBranch(BaseRelatableNode, ABC):
```

### Inherits From
- `BaseRelatableNode`: Provides base functionalities related to node relationships within the system.
- `ABC` (Abstract Base Class): Marks `BaseBranch` as an abstract class, intended to be subclassed.

## Attributes

- `messages` (`pd.DataFrame`): Holds the messages in the branch.
- [[Schema/Data Logger|datalogger]] (`DataLogger`): Logs data related to the branch's operation.
- `persist_path` (`Path | str`): Filesystem path for data persistence.

## Constructor

```python
def __init__(self, messages: pd.DataFrame | None = None, datalogger: DataLogger | None = None, persist_path: Path | str | None = None, **kwargs) -> None:
```

Initializes a new instance of the `BaseBranch` class.

### Parameters

- `messages`: A `pandas.DataFrame` object containing the branch's messages. Defaults to `None`.
- `datalogger`: An instance of `DataLogger` for logging branch operations. Defaults to `None`.
- `persist_path`: A filesystem path where branch data can be persisted. Defaults to `None`.
- `**kwargs`: Additional keyword arguments.

## Core Methods

### add_message

```python
def add_message(self, system: Dict | List | System | None = None, instruction: Dict | List | Instruction | None = None, context: str | Dict[str, Any] | None = None, response: Dict | List | BaseMessage | None = None, **kwargs) -> None:
```

Adds a message to the branch.

#### Parameters

- `system`: Information for creating a System message.
- `instruction`: Information for creating an Instruction message.
- `context`: Context information for the message.
- `response`: Response data for creating a message.
- `**kwargs`: Additional keyword arguments for message creation.


## Properties

### chat_messages

```python
@property
def chat_messages(self) -> List[Dict[str, Any]]:
```

Retrieves all chat messages without sender information.

### chat_messages_with_sender

```python
@property
def chat_messages_with_sender(self) -> List[Dict[str, Any]]:
```

Retrieves all chat messages, including sender information.

### last_message

```python
@property
def last_message(self) -> pd.DataFrame:
```

Retrieves the last message from the branch as a pandas Series.

### last_message_content

```python
@property
def last_message_content(self) -> Dict[str, Any]:
```

Extracts the content of the last message in the branch.

### first_system

```python
@property
def first_system(self) -> pd.DataFrame:
```

Retrieves the first message marked with the 'system' role.

### last_response

```python
@property
def last_response(self) -> pd.DataFrame:
```

Retrieves the last message marked with the 'assistant' role.

### last_response_content

```python
@property
def last_response_content(self) -> Dict[str, Any]:
```

Extracts the content of the last 'assistant' (response) message.

### action_request

```python
@property
def action_request(self) -> pd.DataFrame:
```

Filters and retrieves all messages sent by 'action_request'.

### action_response

```python
@property
def action_response(self) -> pd.DataFrame:
```

Filters and retrieves all messages sent by 'action_response'.

### responses

```python
@property
def responses(self) -> pd.DataFrame:
```

Retrieves all messages marked with the 'assistant' role.



### assistant_responses

```python
@property
def assistant_responses(self) -> pd.DataFrame:
```

Filters 'assistant' role messages excluding 'action_request' and 'action_response'.

### info

```python
@property
def info(self) -> Dict[str, Any]:
```

Summarizes branch information, including message counts by role.

### sender_info

```python
@property
def sender_info(self) -> Dict[str, int]:
```

Provides a summary of message counts categorized by sender.

### describe

```python
@property
def describe(self) -> Dict[str, Any]:
```

Provides a detailed description of the branch, including a summary of messages.

### Data Export and Manipulation Methods

#### to_csv

```python
def to_csv(self, filepath: str | Path = "messages.csv", file_exist_ok: bool = False, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, **kwargs) -> None:
```

Exports the branch messages to a CSV file.

#### to_json

```python
def to_json(self, filename: str | Path = "messages.json", file_exist_ok: bool = False, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, **kwargs) -> None:
```

Exports the branch messages to a JSON file.

#### log_to_csv

```python
def log_to_csv(self, filename: str | Path = "log.csv", file_exist_ok: bool = False, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, **kwargs) -> None:
```

Exports the data logger contents to a CSV file.

#### log_to_json

```python
def log_to_json(self, filename: str | Path = "log.json", file_exist_ok: bool = False, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, **kwargs) -> None:
```

Exports the data logger contents to a JSON file.

## Message Manipulation Methods

### remove_message

```python
def remove_message(self, node_id: str) -> None:
```

Removes a message from the branch based on its node ID.

### update_message

```python
def update_message(self, node_id: str, col: str, value: Any) -> bool:
```

Updates a specific column of a message identified by node_id with a new value.

### rollback

```python
def rollback(self, steps: int) -> None:
```

Removes the last 'n' messages from the branch.

### clear_messages

```python
def clear_messages(self) -> None:
```

Clears all messages from the branch.
