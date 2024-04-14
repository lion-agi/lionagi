# Messaging System API Reference

## BaseMessage

Represents a message in a chatbot-like system, inheriting from BaseNode.

### Attributes
- `role` (str | None): The role of the entity sending the message, e.g., 'user', 'system'.
- `sender` (str | None): The identifier of the sender of the message.
- `recipient` (str | None): The identifier of the recipient of the message.

### Properties
- `msg` (dict): Returns a dictionary representation of the message with 'role' and 'content' keys.
- `msg_content` (str | dict): Gets the 'content' field of the message.

### Methods
- `_to_message()`: Constructs and returns a dictionary representation of the message.
- `__str__()`: Returns a string representation of the message.

## Instruction

^69c0d6

Represents an instruction message, a specialized subclass of Message.

### Attributes
- `instruction` (dict | list | str): The instruction content.
- `context` (Any, optional): The context associated with the instruction.
- `sender` (str | None, optional): The identifier of the sender of the instruction message. Defaults to 'user'.
- `output_fields` (Any, optional): The output fields for the instruction response format.
- `recipient` (str | None, optional): The identifier of the recipient of the instruction message. Defaults to 'assistant'.

### Properties
- `instruct` (Any): Returns the instruction content.

### Class Methods
- `from_prompt_template(prompt_template: PromptTemplate, sender: str | None = None, recipient=None) -> Instruction`: Creates an instruction message from a PromptTemplate.

## System

^9d4814

Represents a system-related message, a specialized subclass of Message.

### Attributes
- `system` (dict | list | str): The system information content.
- `sender` (str | None, optional): The identifier of the sender of the system message. Defaults to 'system'.
- `recipient` (str | None, optional): The identifier of the recipient of the system message. Defaults to 'assistant'.

### Properties
- `system_info` (Any): Returns the system information content.

## Response

Represents a response message, a specialized subclass of Message.

### Attributes
- `response` (dict | list | str): The response content.
- `sender` (str | None, optional): The identifier of the sender of the response message.
- `recipient` (str | None, optional): The identifier of the recipient of the response message.

### Static Methods
- `_handle_action_request(response: dict) -> list`: Processes an action request response and extracts relevant information.

## Enums

### BranchColumns
- `COLUMNS` (list[str]): The list of message fields.

### MessageField
- `NODE_ID` (str): The field for the node ID.
- `TIMESTAMP` (str): The field for the timestamp.
- `ROLE` (str): The field for the role.
- `SENDER` (str): The field for the sender.
- `RECIPIENT` (str): The field for the recipient.
- `CONTENT` (str): The field for the content.
- `METADATA` (str): The field for the metadata.
- `RELATION` (str): The field for the relation.

### MessageRoleType
- `SYSTEM` (str): The role type for system messages.
- `USER` (str): The role type for user messages.
- `ASSISTANT` (str): The role type for assistant messages.

### MessageContentKey
- `INSTRUCTION` (str): The content key for instruction messages.
- `CONTEXT` (str): The content key for context messages.
- `SYSTEM` (str): The content key for system messages.
- `ACTION_REQUEST` (str): The content key for action request messages.
- `ACTION_RESPONSE` (str): The content key for action response messages.
- `RESPONSE` (str): The content key for response messages.

### MessageType
- `SYSTEM` (dict): The message type for system messages.
- `INSTRUCTION` (dict): The message type for instruction messages.
- `CONTEXT` (dict): The message type for context messages.
- `ACTION_REQUEST` (dict): The message type for action request messages.
- `ACTION_RESPONSE` (dict): The message type for action response messages.
- `RESPONSE` (dict): The message type for response messages.