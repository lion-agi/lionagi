
### Class: `Worker`

**Description**:
`Worker` is an abstract base class that manages multiple work functions. It allows for stopping work functions, checking if they are progressable, and processing them periodically.

### Attributes:

- `name` (str): The name of the worker. Default is `"Worker"`.
- `work_functions` (dict[str, WorkFunction]): Dictionary mapping assignments to `WorkFunction` objects.

### Methods:

#### `__init__`

**Signature**:
```python
def __init__(self) -> None
```

**Description**:
Initializes a `Worker` instance. Sets the `stopped` attribute to `False`.

#### `stop`

**Signature**:
```python
async def stop(self)
```

**Description**:
Stops the worker and all associated work functions. Logs the stopping process and any work functions that could not be stopped.

**Usage Example**:
```python
await worker.stop()
```

#### `is_progressable`

**Signature**:
```python
async def is_progressable(self) -> bool
```

**Returns**:
- `bool`: `True` if any work function is progressable and the worker is not stopped, otherwise `False`.

**Description**:
Checks if any work function is progressable and the worker is not stopped.

**Usage Example**:
```python
progressable = await worker.is_progressable()
```

#### `process`

**Signature**:
```python
async def process(self, refresh_time=1)
```

**Parameters**:
- `refresh_time` (int): Time interval between each process cycle.

**Description**:
Processes all work functions periodically. Continues processing as long as any work function is progressable and the worker is not stopped.

**Usage Example**:
```python
await worker.process(refresh_time=2)
```

#### `_wrapper`

**Signature**:
```python
async def _wrapper(
    self,
    *args,
    func=None,
    assignment=None,
    capacity=None,
    retry_kwargs=None,
    guidance=None,
    **kwargs,
)
```

**Parameters**:
- `func` (Callable): The function to be executed.
- `assignment` (str): The assignment description.
- `capacity` (int): Capacity for the work log.
- `retry_kwargs` (dict): Retry arguments for the function.
- `guidance` (str): Guidance or documentation for the function.

**Description**:
Internal wrapper to handle work function execution. Adds the work function to `work_functions` if it does not exist, creates a task to perform the function, and appends the work to the work log.

**Usage Example**:
```python
await worker._wrapper(func=my_function, assignment="My Task", capacity=10)
```

### Decorator: `work`

**Description**:
A decorator to mark a method as a work function. It allows setting parameters such as assignment, capacity, guidance, retry arguments, refresh time, and timeout.

**Parameters**:
- `assignment` (str): The assignment description of the work function.
- `capacity` (int): Capacity for the work log. Default is `10`.
- `guidance` (str): Guidance or documentation for the work function.
- `retry_kwargs` (dict): Retry arguments for the work function.
- `refresh_time` (int): Time interval between each process cycle. Default is `1`.
- `timeout` (int): Timeout for the work function. Default is `10`.

**Usage Example**:
```python
@work(assignment="Example Task", capacity=5, guidance="Example guidance.")
async def example_function(self):
    # Function implementation
    pass
```

### Example Usage

```python
class MyWorker(Worker):
    def __init__(self):
        super().__init__()
        self.name = "MyWorker"

    @work(assignment="Task A", capacity=5)
    async def task_a(self):
        # Task A implementation
        print("Task A is being executed")

    @work(assignment="Task B", capacity=10)
    async def task_b(self):
        # Task B implementation
        print("Task B is being executed")

# Example usage
async def main():
    worker = MyWorker()
    await worker.task_a()
    await worker.task_b()
    await worker.process(refresh_time=2)

asyncio.run(main())
```
