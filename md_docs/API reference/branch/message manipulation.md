

### Class: `MessageUtil`

A utility class containing static methods for creating, validating, filtering, and manipulating messages in a DataFrame format.

##### `create_message`
`(system: System | CUSTOM_TYPE = None, instruction: Instruction | CUSTOM_TYPE = None, context: str | dict[str, Any] | None = None, response: Response | CUSTOM_TYPE = None, output_fields=None, **kwargs) -> BaseMessage`


Creates a message object based on the input parameters, ensuring only one message role is present.

Parameters:
- `system` (`System | CUSTOM_TYPE`): Information for creating a System message (`default: None`).
- `instruction` (`Instruction | CUSTOM_TYPE`): Information for creating an Instruction message (`default: None`).
- `context` (`str | dict[str, Any] | None`): Context information for the message (`default: None`).
- `response` (`Response | CUSTOM_TYPE`): Response data for creating a message (`default: None`).
- `output_fields` (Any): Output fields for the message (`default: None`).
- `**kwargs`: Additional keyword arguments for message creation.

Returns:
BaseMessage: A message object of the appropriate type based on provided inputs.

Raises:
- `ValueError`: If more than one of the role-specific parameters are provided.

##### `validate_messages`
`(messages: dataframe.ln_DataFrame) -> bool`
Validates the format and content of a DataFrame containing messages.

Parameters:
- `messages` (`dataframe.ln_DataFrame`): A DataFrame with message information.

Returns:
bool: True if the messages DataFrame is correctly formatted, False otherwise.

Raises:
- `ValueError`: If the DataFrame does not match expected schema or content requirements.

##### `sign_message`
`(messages: dataframe.ln_DataFrame, sender: str) -> dataframe.ln_DataFrame`
Appends a sender prefix to the 'content' field of each message in a DataFrame.

Parameters:
- `messages` (`dataframe.ln_DataFrame`): A DataFrame containing message data.
- `sender` (str): The identifier of the sender to prefix to message contents.

Returns:
`dataframe.ln_DataFrame`: A DataFrame with sender-prefixed message contents.

Raises:
- `ValueError`: If the sender is None or the value is 'none'.

##### `filter_messages_by`
`(messages: dataframe.ln_DataFrame, role: str | None = None, sender: str | None = None, start_time: `datetime | None` = None, end_time: `datetime | None` = None, content_keywords: str | list[str] | None = None, case_sensitive: bool = False) -> dataframe.ln_DataFrame`
Filters messages in a DataFrame based on specified criteria.

Parameters:
- `messages` (`dataframe.ln_DataFrame`): The DataFrame to filter.
- `role` (str | None): The role to filter by (`default: None`).
- `sender` (str | None): The sender to filter by (`default: None`).
- `start_time` (`datetime | None`): The minimum timestamp for messages (`default: None`).
- `end_time` (`datetime | None`): The maximum timestamp for messages (`default: None`).
- `content_keywords` (`str | list[str] | None`): Keywords to look for in message content (`default: None`).
- `case_sensitive` (bool): Whether the keyword search should be case-sensitive (default: False).

Returns:
`dataframe.ln_DataFrame`: A filtered DataFrame based on the specified criteria.

##### `remove_message`
`(messages: dataframe.ln_DataFrame, node_id: str) -> bool`
Removes a message from the DataFrame based on its node ID.

Parameters:
- `messages` (`dataframe.ln_DataFrame`): The DataFrame containing messages.
- `node_id` (str): The unique identifier of the message to be removed.

Returns:
bool: True if any messages are removed, False otherwise.

##### `get_message_rows`
`(messages: dataframe.ln_DataFrame, sender: str | None = None, role: str | None = None, n: int = 1, sign_: bool = False, from_: str = "front") -> dataframe.ln_DataFrame`
Retrieves a specified number of message rows based on sender and role.

Parameters:
- `messages` (`dataframe.ln_DataFrame`): The DataFrame containing messages.
- `sender` (str | None): Filter messages by the sender (`default: None`).
- `role` (str | None): Filter messages by the role (`default: None`).
- `n` (int): The number of messages to retrieve (default: 1).
- `sign_` (bool): If True, sign the message with the sender (default: False).
- `from_` (str): Specify retrieval from the 'front' or 'last' of the DataFrame (default: "front").

Returns:
`dataframe.ln_DataFrame`: A DataFrame containing the filtered messages.

##### `extend`
`(df1: dataframe.ln_DataFrame, df2: dataframe.ln_DataFrame, **kwargs) -> dataframe.ln_DataFrame`
Extends a DataFrame with another DataFrame's rows, ensuring no duplicate 'node_id'.

Parameters:
- `df1` (`dataframe.ln_DataFrame`): The primary DataFrame.
- `df2` (`dataframe.ln_DataFrame`): The DataFrame to merge with the primary DataFrame.
- `**kwargs`: Additional keyword arguments for `drop_duplicates`.

Returns:
`dataframe.ln_DataFrame`: A DataFrame combined from df1 and df2 with duplicates removed based on 'node_id'.

##### `to_markdown_string`
`(messages: dataframe.ln_DataFrame) -> str`
Converts messages in a DataFrame to a Markdown-formatted string for easy reading.

Parameters:
- `messages` (`dataframe.ln_DataFrame`): A DataFrame containing messages with columns for 'role' and 'content'.

Returns:
str: A string formatted in Markdown, where each message's content is presented according to its role in a readable format.

### Usage Example
```python
from lionagi.core.messages.util import MessageUtil
from lionagi.core.messages.schema import System, Instruction, Response
from lionagi.libs.dataframe import ln_DataFrame

# Create messages
system_msg = System(system="System message")
instruction_msg = Instruction(instruction="Instruction message", context="Context")
response_msg = Response(response="Response message")

# Create a message using MessageUtil
message = MessageUtil.create_message(system=system_msg)

# Create a DataFrame with messages
messages_df = ln_DataFrame([system_msg.to_dict(), instruction_msg.to_dict(), response_msg.to_dict()])

# Validate messages DataFrame
is_valid = MessageUtil.validate_messages(messages_df)

# Filter messages by criteria
filtered_messages = MessageUtil.filter_messages_by(messages_df, role="system", sender="sender_id")

# Remove a message by node ID
removed = MessageUtil.remove_message(messages_df, node_id="node_id_123")

# Get message rows by sender and role
message_rows = MessageUtil.get_message_rows(messages_df, sender="sender_id", role="user", n=2)

# Extend a DataFrame with another DataFrame
extended_df = MessageUtil.extend(messages_df, ln_DataFrame([system_msg.to_dict(), instruction_msg.to_dict()]))

# Convert messages to Markdown string
markdown_string = MessageUtil.to_markdown_string(messages_df)
```

In this example, we demonstrate the usage of various utility functions provided by the `MessageUtil` class. We create messages using the `System`, `Instruction`, and `Response` classes, and then use `MessageUtil.create_message()` to create a message based on input parameters.

We create a DataFrame with messages and use `MessageUtil.validate_messages()` to validate the DataFrame format and content. We filter messages based on criteria using `MessageUtil.filter_messages_by()`, remove a message by its node ID using `MessageUtil.remove_message()`, and retrieve message rows based on sender and role using `MessageUtil.get_message_rows()`.

We extend a DataFrame with another DataFrame using `MessageUtil.extend()` and convert the messages to a Markdown-formatted string using `MessageUtil.to_markdown_string()`.
