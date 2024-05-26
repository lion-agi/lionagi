
### Class: `WorkLog`

**Description**:
`WorkLog` is a class that represents a log of work items. It manages the collection of work items, their progression, and the queue for executing these work items.

### Attributes:

- `pile` (Pile): A pile containing work items.
- `pending` (Progression): A progression of pending work items.
- `queue` (WorkQueue): A queue to manage the execution of work items.

### Methods:

#### `__init__`

**Signature**:
```python
def __init__(self, capacity=10, workpile=None)
```

**Parameters**:
- `capacity` (int): The capacity of the work queue. Default is `10`.
- `workpile` (Pile, optional): An optional pile of initial work items.

**Description**:
Initializes a new instance of `WorkLog` with an optional initial pile of work items and a specified queue capacity.

**Usage Example**:
```python
worklog = WorkLog(capacity=15)
```

#### `append`

**Signature**:
```python
async def append(self, work: Work)
```

**Parameters**:
- `work` (Work): The work item to append.

**Description**:
Appends a new work item to the log, adding it to both the `pile` and the `pending` progression.

**Usage Example**:
```python
await worklog.append(work_item)
```

#### `forward`

**Signature**:
```python
async def forward(self)
```

**Description**:
Forwards pending work items to the queue if the queue's capacity allows.

**Usage Example**:
```python
await worklog.forward()
```

#### `stop`

**Signature**:
```python
async def stop(self)
```

**Description**:
Stops the work queue, signaling it to cease processing.

**Usage Example**:
```python
await worklog.stop()
```

#### `pending_work`

**Signature**:
```python
@property
def pending_work(self) -> Pile
```

**Returns**:
- `Pile`: A pile of pending work items.

**Description**:
Retrieves the pile of pending work items.

**Usage Example**:
```python
pending = worklog.pending_work
```

#### `stopped`

**Signature**:
```python
@property
def stopped(self) -> bool
```

**Returns**:
- `bool`: `True` if the work queue is stopped, else `False`.

**Description**:
Checks if the work queue is stopped.

**Usage Example**:
```python
is_stopped = worklog.stopped
```

#### `completed_work`

**Signature**:
```python
@property
def completed_work(self) -> Pile
```

**Returns**:
- `Pile`: A pile of completed work items.

**Description**:
Retrieves the pile of completed work items.

**Usage Example**:
```python
completed = worklog.completed_work
```

#### `__contains__`

**Signature**:
```python
def __contains__(self, work: Work) -> bool
```

**Parameters**:
- `work` (Work): The work item to check.

**Returns**:
- `bool`: `True` if the work item is in the pile, else `False`.

**Description**:
Checks if a work item is in the pile.

**Usage Example**:
```python
is_in_pile = work_item in worklog
```

#### `__iter__`

**Signature**:
```python
def __iter__(self) -> Iterator
```

**Returns**:
- `Iterator`: An iterator over the work pile.

**Description**:
Returns an iterator over the work pile.

**Usage Example**:
```python
for work_item in worklog:
    print(work_item)
```

### Example Usage

```python
# Create a WorkLog with a capacity of 15
worklog = WorkLog(capacity=15)

# Create a Work item
work_item = Work()

# Append the Work item to the WorkLog
await worklog.append(work_item)

# Forward pending work items to the queue
await worklog.forward()

# Check if a Work item is in the WorkLog
if work_item in worklog:
    print("Work item is in the log")

# Iterate over work items in the WorkLog
for item in worklog:
    print(item)

# Retrieve pending and completed work items
pending = worklog.pending_work
completed = worklog.completed_work

# Stop the WorkLog
await worklog.stop()
```

This structure provides a comprehensive overview of the `WorkLog` class, detailing its attributes, methods, and usage examples to ensure clear understanding and practical application.
