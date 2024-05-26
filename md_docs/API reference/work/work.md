
### Class: `Work`

**Description**:
`Work` is a class representing a unit of work with various attributes to track its status, result, errors, and duration. It also includes a method to perform the work asynchronously and update the relevant attributes.

### Attributes:

- `status` (WorkStatus): The current status of the work. Defaults to `WorkStatus.PENDING`.
- `result` (Any): The result of the work, if completed. Defaults to `None`.
- `error` (Any): Any error encountered during the work. Defaults to `None`.
- `async_task` (asyncio.Task | None): The asynchronous task associated with the work. Defaults to `None`.
- `completion_timestamp` (str | None): The timestamp when the work was completed. Defaults to `None`.
- `duration` (float | None): The duration of the work. Defaults to `None`.

### Methods:

#### `perform`

**Signature**:
```python
async def perform(self)
```

**Description**:
Asynchronously performs the work and updates the status, result, and duration. It handles any exceptions that occur during the execution and sets the error attribute accordingly.

**Raises**:
- `Exception`: If an error occurs during the execution of the work.

**Usage Example**:
```python
# Assuming 'some_async_task' is a coroutine that performs a task and returns a result and duration
work_instance = Work(async_task=some_async_task)
await work_instance.perform()
print(work_instance.status)  # Output: WorkStatus.COMPLETED or WorkStatus.FAILED
print(work_instance.result)  # Output: Result of the task if completed
print(work_instance.error)   # Output: Error if the task failed
print(work_instance.duration)  # Output: Duration of the task if completed
print(work_instance.completion_timestamp)  # Output: Timestamp when the task was completed
```

#### `__str__`

**Signature**:
```python
def __str__(self)
```

**Returns**:
- `str`: A string representation of the work instance.

**Description**:
Provides a string representation of the work instance, including the ID, status, creation timestamp, completion timestamp, and duration.

**Usage Example**:
```python
work_instance = Work()
print(str(work_instance))  # Output: Work(id=..., status=..., created_at=..., completed_at=..., duration=...)
```

### Enum: `WorkStatus`

**Description**:
An enumeration representing different statuses of work.

### Values:

- `PENDING`: Represents work that is pending.
- `IN_PROGRESS`: Represents work that is in progress.
- `COMPLETED`: Represents work that is completed.
- `FAILED`: Represents work that has failed.

**Usage Example**:
```python
status = WorkStatus.PENDING
print(status)  # Output: WorkStatus.PENDING
```
