
This module contains the `BaseAgent` class, which serves as a base class for agents.

## Class: `BaseAgent`

A base class for agents.

Attributes:
- `structure`: The [[structure executor]] of the agent.
- `executable`: The [[branch executor|executor]] object of the agent.
- `start`: The [[API reference/mail/mail#^389d46|StartMail]] object for triggering the agent.
- `mailManager`: The [[mail manager]] object for managing agent communication.
- `output_parser`: A function for parsing the agent's output (optional).
- `start_context`: The initial context for the agent (optional).

### Methods:

#### `__init__`
`(self, structure, executable_obj, output_parser=None) -> None`
Initializes the `BaseAgent` instance.

Parameters:
- `structure`: The structure of the agent.
- `executable_obj`: The executable object of the agent.
- `output_parser`: A function for parsing the agent's output (optional).

#### `async mail_manager_control`
`(self, refresh_time=1) -> None`
Controls the [[mail manager]] execution based on the structure and executable states.

Parameters:
- `refresh_time`: The time interval (in seconds) for checking the execution states (default: 1).

#### `async execute`
`(self, context=None) -> Any`
Executes the agent with the given context and returns the parsed output (if available).

Parameters:
- `context`: The initial context for the agent (optional).

Returns:
The parsed output of the agent (if available).
