# lionagi.protocols.generic.processor


### Constructor

#### __init__(processor_config=None, strict_event_type=False)
Initialize executor.

Parameters:
- **processor_config** (*dict | None*) - Processor settings
- **strict_event_type** (*bool*) - Enforce event types

Example:
```python
>>> executor = Executor(processor_config={
...     "queue_capacity": 10,
...     "capacity_refresh_time": 1.0
... })
```

### Properties

#### completed_events
Events that completed successfully.

Type:
- Pile[Event]

Example:
```python
>>> for event in executor.completed_events:
...     print(event.response)
```

#### failed_events
Events that failed processing.

Type:
- Pile[Event]

Example:
```python
>>> for event in executor.failed_events:
...     print(event.execution.error)
```

#### pending_events
Events waiting to be processed.

Type:
- Pile[Event]

Example:
```python
>>> if executor.pending_events:
...     await executor.forward()
```

### Methods

#### async append(event)
Add new event for processing.

Parameters:
- **event** (*Event*) - Event to process

Example:
```python
>>> await executor.append(event)
```

#### async forward()
Process all pending events.

Example:
```python
>>> await executor.append(event)
>>> await executor.forward()  # Process immediately
```

#### async start()
Initialize and start processor.

Example:
```python
>>> await executor.start()
>>> await executor.append(event)  # Auto-processed
```

#### async stop()
Stop processor if running.

Example:
```python
>>> await executor.stop()  # Graceful shutdown
```

## Error Handling

```python
# Handle capacity errors
try:
    processor = Processor(queue_capacity=0)  # Invalid
except ValueError as e:
    print(f"Invalid capacity: {e}")

# Handle processing errors    
try:
    await processor.process()
except Exception as e:
    print(f"Processing failed: {e}")
```
Asynchronous event processing system with capacity management.

This module provides:
- Async event processing with queue management
- Capacity control and refresh
- Event execution tracking

Example:
    >>> from lionagi.protocols.generic import Processor
    >>> processor = Processor(queue_capacity=10, capacity_refresh_time=1.0)
    >>> await processor.enqueue(event)
    >>> await processor.process()
"""

## Processor

Async event processor with capacity management.

```python
class Processor(Observer):
    """Event processor with queue and capacity control.
    
    Example:
        >>> processor = Processor(queue_capacity=10, capacity_refresh_time=1.0)
        >>> await processor.start()
        >>> await processor.enqueue(event)
        >>> await processor.stop()
    """
    event_type: ClassVar[type[Event]]  # Event class handled
```

### Constructor

#### __init__(queue_capacity, capacity_refresh_time)
Initialize processor with capacity settings.

Parameters:
- **queue_capacity** (*int*) - Maximum events per batch
- **capacity_refresh_time** (*float*) - Seconds between resets

Raises:
- ValueError - Invalid capacity values

Example:
```python
>>> processor = Processor(queue_capacity=100, capacity_refresh_time=0.5)
```

### Properties

#### available_capacity
Current available processing slots.

Type:
- int

Example:
```python
>>> if processor.available_capacity > 0:
...     await processor.enqueue(event)
```

#### execution_mode
Whether processor is actively executing.

Type:
- bool

Example:
```python
>>> if not processor.execution_mode:
...     await processor.start()
```

### Methods

#### async enqueue(event)
Add event to processing queue.

Parameters:
- **event** (*Event*) - Event to process

Example:
```python
>>> await processor.enqueue(event)
```

#### async dequeue()
Get next event from queue.

Returns:
- Event - Next event to process

Example:
```python
>>> event = await processor.dequeue()
>>> if event is not None:
...     await process_event(event)
```

#### async process()
Process events up to capacity limit.

Example:
```python
>>> await processor.process()
```

#### async execute()
Continuously process events until stopped.

Example:
```python
>>> asyncio.create_task(processor.execute())
>>> await processor.enqueue(event)
```

#### async start()
Begin or resume processing.

Example:
```python
>>> await processor.start()
>>> await processor.enqueue(event)
```

#### async stop()
Signal processing to stop.

Example:
```python
>>> await processor.stop()
>>> await processor.join()  # Wait for completion
```

## Executor

Event manager with storage.

```python
class Executor(Observer):
    """Event processing manager.
    
    Example:
        >>> executor = Executor(processor_config={
        ...     "queue_capacity": 10,
        ...     "capacity_refresh_time": 1.0
        ... })
        >>> await executor.append(event)
        >>> await executor.forward()
    """
