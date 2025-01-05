# lionagi.protocols.generic.event

"""
Execution state tracking system for async operations.

This module provides:
- Event status tracking
- Execution state management
- Result/error handling

Example:
    >>> from lionagi.protocols.generic import Event, EventStatus
    >>> event = Event()
    >>> event.status
    <EventStatus.PENDING>
    >>> event.execution.error is None
    True
"""

## EventStatus

Execution state enumeration.

```python
class EventStatus(str, Enum):
    """Event execution states.
    
    Example:
        >>> status = EventStatus.PENDING
        >>> status == "pending"
        True
    """
    PENDING = "pending"      # Initial state
    PROCESSING = "processing"  # Currently executing
    COMPLETED = "completed"    # Successfully finished
    FAILED = "failed"         # Execution failed
```

## Execution

Event execution state container.

```python
class Execution:
    """Container for execution state.
    
    Example:
        >>> exec = Execution()
        >>> exec.status
        <EventStatus.PENDING>
        >>> exec.duration is None
        True
    """
```

### Attributes

#### status
Current execution state.

Type:
- EventStatus

#### duration
Execution time in seconds.

Type:
- float | None

#### response
Execution result if successful.

Type:
- Any

#### error
Error message if failed.

Type:
- str | None

## Event

Base event with execution tracking.

```python
class Event(Element):
    """Base class for trackable events.
    
    Example:
        >>> event = Event()
        >>> event.status
        <EventStatus.PENDING>
        >>> await event.invoke()  # Must override
        Traceback (most recent call last):
            ...
        NotImplementedError: Override in subclass
    """
```

### Attributes

#### execution
Execution state container.

Type:
- Execution

### Properties

#### response
Get/set execution response.

Type:
- Any

Example:
```python
>>> event = Event()
>>> event.response = "result"
>>> event.execution.response
'result'
```

#### status
Get/set execution status.

Type:
- EventStatus

Example:
```python
>>> event = Event()
>>> event.status = EventStatus.PROCESSING
>>> event.execution.status
<EventStatus.PROCESSING>
```

#### request
Get event request parameters.

Returns:
- dict - Empty by default, override in subclasses

### Methods

#### async invoke()
Execute event action.

Raises:
- NotImplementedError - Must override in subclass

Example:
```python
>>> class CustomEvent(Event):
...     async def invoke(self):
...         self.status = EventStatus.PROCESSING
...         try:
...             result = await do_work()
...             self.response = result
...             self.status = EventStatus.COMPLETED
...         except Exception as e:
...             self.status = EventStatus.FAILED
...             self.execution.error = str(e)
```

## Error Handling

```python
# Track execution status
try:
    await event.invoke()
except Exception as e:
    print(f"Execution error: {e}")
finally:
    if event.status == EventStatus.FAILED:
        print(f"Failed: {event.execution.error}")
```
