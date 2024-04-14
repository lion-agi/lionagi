The provided code defines a `DataLogger` class for managing and persisting log entries in an application. Here's a breakdown of the main components:

1. `DLog` dataclass:
   - Represents a log entry with `input_data` and `output_data` fields.
   - Provides methods for serializing and deserializing log entries.

2. `DataLogger` class:
   - Manages the accumulation, structuring, and persistence of log entries.
   - Initializes with optional custom settings for log storage.
   - Provides methods for appending and extending log entries.
   - Supports exporting logs to CSV and JSON files with customizable options.
   - Automatically saves unsaved logs at program exit.

Here's an API reference for the `DataLogger` class:

### Initialization

```python
def __init__(self, persist_path: str | Path | None = None, log: List[Dict] | None = None, filename: str | None = None) -> None:
```

Initializes the `DataLogger` with optional custom settings for log storage.

- `persist_path`: The file system path for storing log files. Defaults to 'data/logs/'.
- `log`: Initial log entries.
- `filename`: Base name for exported log files.

### Methods

#### `extend`

```python
def extend(self, logs) -> None:
```

Extends the log deque with multiple log entries.

- `logs`: A list of log entries, each as a dictionary conforming to the log structure.

#### `append`

```python
def append(self, *, input_data: Any, output_data: Any) -> None:
```

Appends a new log entry from provided input and output data.

- `input_data`: Input data to the operation.
- `output_data`: Output data from the operation.

#### `to_csv_file`

```python
def to_csv_file(self, filename: str = "log.csv", *, dir_exist_ok: bool = True, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, flatten_=True, sep="[^_^]", index=False, **kwargs) -> None:
```

Exports log entries to a CSV file with customizable options.

- `filename`: Filename for the exported CSV. Defaults to 'log.csv'.
- `dir_exist_ok`: If True, allows writing to an existing directory.
- `timestamp`: If True, appends a timestamp to the filename.
- `time_prefix`: If True, places the timestamp prefix before the filename.
- `verbose`: If True, prints a message upon successful save.
- `clear`: If True, clears the log deque after saving.
- `flatten_`: If True, flattens dictionary data for serialization.
- `sep`: Separator for flattening nested dictionaries.
- `index`: If True, includes an index column in the CSV.
- `**kwargs`: Additional arguments for DataFrame.to_csv().

#### `to_json_file`

```python
def to_json_file(self, filename: str = "log.json", *, dir_exist_ok: bool = True, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, flatten_=True, sep="[^_^]", index=False, **kwargs) -> None:
```

Exports log entries to a JSON file with customizable options.

- `filename`: Filename for the exported JSON. Defaults to 'log.json'.
- `dir_exist_ok`: If True, allows writing to an existing directory.
- `timestamp`: If True, appends a timestamp to the filename.
- `time_prefix`: If True, places the timestamp prefix before the filename.
- `verbose`: If True, prints a message upon successful save.
- `clear`: If True, clears the log deque after saving.
- `flatten_`: If True, flattens dictionary data for serialization.
- `sep`: Separator for flattening nested dictionaries.
- `index`: If True, includes an index in the JSON.
- `**kwargs`: Additional arguments for DataFrame.to_json().

#### `save_at_exit`

```python
def save_at_exit(self):
```

Registers an at-exit handler to automatically persist unsaved logs to a file upon program termination.

The `DataLogger` class provides a convenient way to manage and persist log entries in an application. It supports appending and extending log entries, exporting logs to CSV and JSON files with customizable options, and automatically saving unsaved logs at program exit.
