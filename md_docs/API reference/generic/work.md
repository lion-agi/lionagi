## Work Class

Represents a unit of work, encapsulating completion status and result.

### Attributes
- `work_completed (bool)`: A flag indicating whether the work is already completed.
- `work_result (Any | None)`: The result of the work, if any.
- `context (dict | str | None)`: The context buffer for the next instruction, providing additional details or state needed for subsequent actions.

## Worker Class

Extends the Node class and serves as an abstract base class for worker nodes within the system.

### Attributes
- `stopped (bool)`: Indicates whether the worker is stopped.

### Methods
- `perform(*args, **kwargs)`: Abstract method to perform the assigned task.
- `forward(*args, **kwargs)`: Abstract method to forward the process after performing the work.
- `stop()`: Stops the worker and sets the `stopped` flag to True.

### Description
The Worker class defines the fundamental operations required for a worker node, including methods to perform and forward work, as well as to stop the worker. It requires concrete implementations of the `perform` and `forward` methods in subclasses.
