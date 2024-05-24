
### Class: `WorkQueue`

**Description**:
`WorkQueue` is a class designed to manage a queue of work items. It supports enqueuing, dequeuing, processing tasks concurrently, and managing the capacity of the queue. The queue can be stopped gracefully, and it ensures that all tasks are processed before stopping.

### Attributes:

- `capacity` (int): The maximum number of tasks the queue can handle. Defaults to 5.
- `queue` (asyncio.Queue): The queue holding the tasks.
- `_stop_event` (asyncio.Event): Event to signal stopping of the queue.
- `semaphore` (asyncio.Semaphore): Semaphore to control access based on capacity.

### Methods:

#### `__init__`

**Signature**:
```python
def __init__(self, capacity=5)
```

**Parameters**:
- `capacity` (int, optional): The maximum number of tasks the queue can handle. Defaults to `5`.

**Description**:
Initializes a `WorkQueue` instance with the specified capacity. Sets up the queue, stop event, and semaphore.

#### `enqueue`

**Signature**:
```python
async def enqueue(self, work) -> None
```

**Parameters**:
- `work` (Any): The work item to be enqueued.

**Description**:
Asynchronously enqueues a work item into the queue.

**Usage Example**:
```python
await work_queue.enqueue(work_item)
```

#### `dequeue`

**Signature**:
```python
async def dequeue(self)
```

**Returns**:
- `Any`: The dequeued work item.

**Description**:
Asynchronously dequeues a work item from the queue.

**Usage Example**:
```python
work_item = await work_queue.dequeue()
```

#### `join`

**Signature**:
```python
async def join(self) -> None
```

**Description**:
Blocks until all items in the queue have been processed.

**Usage Example**:
```python
await work_queue.join()
```

#### `stop`

**Signature**:
```python
async def stop(self) -> None
```

**Description**:
Signals the queue to stop processing.

**Usage Example**:
```python
await work_queue.stop()
```

#### `available_capacity`

**Signature**:
```python
@property
def available_capacity(self)
```

**Returns**:
- `int | None`: The available capacity of the queue. Returns `None` if the queue is full.

**Description**:
Returns the available capacity of the queue.

**Usage Example**:
```python
capacity = work_queue.available_capacity
```

#### `stopped`

**Signature**:
```python
@property
def stopped(self) -> bool
```

**Returns**:
- `bool`: `True` if the queue has been stopped, otherwise `False`.

**Description**:
Returns whether the queue has been stopped.

**Usage Example**:
```python
is_stopped = work_queue.stopped
```

#### `process`

**Signature**:
```python
async def process(self) -> None
```

**Description**:
Processes the work items in the queue. It manages tasks concurrently, respects the queue's capacity, and handles stopping gracefully.

**Usage Example**:
```python
await work_queue.process()
```

### Example Usage

```python
import asyncio

class Work:
    async def perform(self):
        print("Work is being performed")
        await asyncio.sleep(1)

async def main():
    work_queue = WorkQueue(capacity=3)
    
    for _ in range(5):
        await work_queue.enqueue(Work())
    
    print("Starting work processing")
    await work_queue.process()
    print("All work processed")

asyncio.run(main())
```
