## Transfer Class

Encapsulates the handling of scheduled transfers of mails and signals within the system.

### Attributes
- `schedule (dict[str, deque[Mail | Signal]])`: The sequence of all pending mails and signals, organized by direction and stored as deques.

### Properties
- `is_empty`: Returns a flag indicating whether the transfer schedule is empty, useful for checking if there are any pending actions.

### Description
The Transfer class provides mechanisms to manage and query the status of mail and signal transfers, enabling efficient scheduling and execution within the system.
