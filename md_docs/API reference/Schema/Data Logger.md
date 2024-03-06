---
tags:
  - "#BaseObj"
  - logs
  - API
created: 2024-02-26
completed: true
---

# Data Logger API Reference

This document provides the API reference for the `DLog` and `DataLogger` classes, which are designed for structured logging of data processing operations.

## DLog Class

> Child class of [`dataclass`](https://docs.python.org/3/library/dataclasses.html)

Represents a log entry, capturing both input to and output from a data processing operation, along with an automatically generated timestamp.

### Attributes

- `input_data`: The data received by the operation. Can be of any type.
- `output_data`: The data produced by the operation. Supports any type.

### Methods

#### `serialize() -> Dict[str, Any]`

Converts the `DLog` instance into a dictionary suitable for serialization. Adds a 'timestamp' key to the dictionary.

**Example:**

```python
log_entry = DLog(input_data="some input", output_data="some output")
serialized_entry = log_entry.serialize()
print(serialized_entry)
# Output includes input_data, output_data, and timestamp
```

## DataLogger Class

Manages the accumulation, structuring, and persistence of log entries related to data processing activities.

### Attributes

- `persist_path`: Path to the directory where log files will be saved.
- `log`: A deque object containing log entries as dictionaries.
- `filename`: The base name for log files when saved.

### Methods

#### `append(input_data: Any, output_data: Any)`

Adds a new log entry to the record.

**Example:**

```python
datalogger = DataLogger()
datalogger.append(input_data="input", output_data="output")
```

#### `to_csv(filename: str, ...) -> None`

Exports accumulated log entries to a CSV file. Supports customization of the output file's name, timestamping, and other CSV options.

**Example:**

```python
datalogger.to_csv('logs.csv', clear=True)
# Exports log entries to 'logs.csv' and clears the log
```

#### `to_json(filename: str, ...) -> None`

Exports log entries to a JSON file within the specified persisting directory. Offers file naming and timestamping customization.

**Example:**

```python
datalogger.to_json('logs.json', clear=True)
# Exports log entries to 'logs.json' and clears the log
```

#### `save_at_exit() -> None`

Ensures any unsaved logs are automatically persisted to a file upon program termination.

**Usage:** Automatically registered upon `DataLogger` instantiation.
