
# MessageUtil API Reference

## Overview

The `MessageUtil` class provides utilities for creating, validating, signing, filtering, and managing messages within a DataFrame structure. This documentation covers the public methods available in the `MessageUtil` class.

## Methods

### `create_message`

Creates a message object based on the input parameters, ensuring only one message role is present.

- **Parameters**:
    - `system`: Information for creating a System message. Can be `dict[str, Any]`, `str`, `List[Any]`, `System`, or `None`.
    - `instruction`: Information for creating an Instruction message. Can be `dict[str, Any]`, `str`, `List[Any]`, `Instruction`, or `None`.
    - `context`: Context information for the message. Can be `str` or `Dict[str, Any]`.
    - `response`: Response data for creating a message. Can be `dict[str, Any]`, `List[Any]`, `str`, `Response`, or `None`.
    - `**kwargs`: Additional keyword arguments for message creation.
- **Returns**: A message object of the appropriate type based on provided inputs.
- **Raises**: `ValueError` if more than one of the role-specific parameters are provided.

#### Example

```python
from lionagi.core.session.base.schema import System, Instruction, Response, BaseMessage
message = MessageUtil.create_message(instruction="This is an instruction.")
```

### `validate_messages`

Validates the format and content of a DataFrame containing messages.

- **Parameters**:
    - `messages`: A DataFrame with message information.
- **Returns**: `True` if the messages DataFrame is correctly formatted, `False` otherwise.
- **Raises**: `ValueError` if the DataFrame does not match expected schema or content requirements.

#### Example

```python
import pandas as pd
messages_df = pd.DataFrame([...])
valid = MessageUtil.validate_messages(messages_df)
```

### `sign_message`

Appends a sender prefix to the 'content' field of each message in a DataFrame.

- **Parameters**:
    - `messages`: A DataFrame containing message data.
    - `sender`: The identifier of the sender to prefix to message contents.
- **Returns**: A DataFrame with sender-prefixed message contents.
- **Raises**: `ValueError` if the sender is `None` or the value is 'none'.

#### Example

```python
import pandas as pd
messages_df = pd.DataFrame([...])
signed_messages_df = MessageUtil.sign_message(messages_df, sender="User")
```



### `filter_messages_by`

Filters messages in a DataFrame based on specified criteria.

- **Parameters**:
    - `messages`: The DataFrame to filter.
    - `role`: The role to filter by. Can be `str` or `None`.
    - `sender`: The sender to filter by. Can be `str` or `None`.
    - `start_time`: The minimum timestamp for messages. Can be `datetime` or `None`.
    - `end_time`: The maximum timestamp for messages. Can be `datetime` or `None`.
    - `content_keywords`: Keywords to look for in message content. Can be `str`, `List[str]`, or `None`.
    - `case_sensitive`: Whether the keyword search should be case-sensitive. Defaults to `False`.
- **Returns**: A filtered DataFrame based on the specified criteria.

#### Example

```python
import pandas as pd
from datetime import datetime
messages_df = pd.DataFrame([...])
filtered_messages_df = MessageUtil.filter_messages_by(messages_df, role="user", start_time=datetime(2021, 1, 1))
```

### `remove_message`

Removes a message from the DataFrame based on its node ID.

- **Parameters**:
    - `messages`: The DataFrame containing messages.
    - `node_id`: The unique identifier of the message to be removed.
- **Returns**: `True` if any messages are removed, otherwise `False`.

#### Example

```python
import pandas as pd
messages_df = pd.DataFrame([...])
updated_messages = MessageUtil.remove_message(messages_df, "node_id_123")
```

### `get_message_rows`

Retrieves a specified number of message rows based on sender and role.

- **Parameters**:
    - `messages`: The DataFrame containing messages.
    - `sender`: Filter messages by the sender. Can be `str` or `None`.
    - `role`: Filter messages by the role. Can be `str` or `None`.
    - `n`: The number of messages to retrieve.
    - `sign_`: If `True`, sign the message with the sender.
    - `from_`: Specify retrieval from the 'front' or 'last' of the DataFrame. Can be `"front"` or `"last"`.
- **Returns**: A DataFrame containing the filtered messages.

#### Example

```python
import pandas as pd
messages_df = pd.DataFrame([...])
selected_messages_df = MessageUtil.get_message_rows(messages_df, sender="User", n=2)
```
