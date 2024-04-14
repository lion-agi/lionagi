
This module contains the `BaseBranch` class, which serves as a base class for managing branches of conversation, incorporating messages and logging functionality.

### Class: `BaseBranch`

parent: [[component#^5b7bda|BaseNode]]

A base class for managing branches of conversation, incorporating messages and logging functionality.

Attributes:
- `messages` (`pd.DataFrame`): Holds the [[message manipulation|conversation message]] in the branch.
- `datalogger` ([[data logger|DataLogger]]): Logs data related to the branch's operation.
- `persist_path` (PATH_TYPE): Filesystem path for data persistence.


### Properties
- `chat_messages` (`list[dict[str, Any]]`): Retrieves all chat messages without sender information.
- `chat_messages_with_sender` (`list[dict[str, Any]]`): Retrieves all chat messages, including sender information.
- `last_message` (`dataframe.ln_DataFrame`): Retrieves the last message from the branch as a pandas Series.
- `last_message_content` (`dict[str, Any]`): Extracts the content of the last message in the branch.
- `first_system` (`dataframe.ln_DataFrame`): Retrieves the first message marked with the 'system' role.
- `last_response` (`dataframe.ln_DataFrame`): Retrieves the last message marked with the 'assistant' role.
- `last_response_content` (`dict[str, Any]`): Extracts the content of the last 'assistant' (response) message.
- `action_request` (`dataframe.ln_DataFrame`): Filters and retrieves all messages sent by 'action_request'.
- `action_response` (`dataframe.ln_DataFrame`): Filters and retrieves all messages sent by 'action_response'.
- `responses` (`dataframe.ln_DataFrame`): Retrieves all messages marked with the 'assistant' role.
- `assistant_responses` (`dataframe.ln_DataFrame`): Filters 'assistant' role messages excluding 'action_request' and 'action_response'.
- `last_assistant_response` (`Any`): Retrieves the last assistant response message.
- `info` (`dict[str, Any]`): Summarizes branch information, including message counts by role.
- `sender_info` (`dict[str, int]`): Provides a summary of message counts categorized by sender.
- `describe` (`dict[str, Any]`): Provides a detailed description of the branch, including a summary of messages.



### Methods
##### `__init__`
`(self, messages: dataframe.ln_DataFrame | None = None, datalogger: DataLogger | None = None, persist_path: PATH_TYPE | None = None, name=None, **kwargs) -> None`
Initializes the `BaseBranch` instance.

Parameters:
- `messages` (`dataframe.ln_DataFrame | None`): The messages to initialize the branch with (default: None).
- `datalogger` (`DataLogger | None`): The data logger to use for logging branch data (default: None).
- `persist_path` (`PATH_TYPE | None`): The filesystem path for data persistence (default: None).
- `name` (str | None): The name of the branch (default: None).
- `**kwargs`: Additional keyword arguments.

##### `add_message`
`(self, system: dict | list | System | None = None, instruction: dict | list | Instruction | None = None, context: str | dict[str, Any] | None = None, response: dict | list | BaseMessage | None = None, output_fields=None, recipient=None, **kwargs) -> None`
Adds a [[messages|message]] to the branch.

Parameters:
- `system` (`dict | list | System | None`): Information for creating a System message (default: None).
- `instruction` (`dict | list | Instruction | None`): Information for creating an Instruction message (default: None).
- `context` (`str | dict[str, Any] | None`): Context information for the message (default: None).
- `response` (`dict | list | BaseMessage | None`): Response data for creating a message (default: None).
- `output_fields` (`Any`): Output fields for the message (default: None).
- `recipient` (`str | None`): The recipient of the message (default: None).
- `**kwargs`: Additional keyword arguments for message creation.

##### `remove_message`
`(self, node_id: str) -> None`
Removes a message from the branch based on its node ID.

Parameters:
- `node_id` (`str`): The unique identifier of the message to be removed.

##### `update_message`
`(self, node_id: str, column: str, value: Any) -> bool`
Updates a specific column of a message identified by node_id with a new value.

Parameters:
- `node_id` (`str`): The unique identifier of the message to update.
- `column` (`str`): The column of the message to update.
- `value` (`Any`): The new value to update the message with.

Returns:
bool: True if the message was updated successfully, False otherwise.

##### `change_first_system_message`
`(self, system: str | dict[str, Any] | System, sender: str | None = None) -> None`
Updates the first system message with new content and/or sender.

Parameters:
- `system` (`str | dict[str, Any] | System`): The new system message content or a System object.
- `sender` (`str | None`): The identifier of the sender for the system message (default: None).

##### `rollback`
`(self, steps: int) -> None`
Removes the last 'n' messages from the branch.

Parameters:
- `steps` (int): The number of messages to remove from the end.

##### `clear_messages`
`(self) -> None`
Clears all messages from the branch.

##### `replace_keyword`
`(self, keyword: str, replacement: str, column: str = "content", case_sensitive: bool = False) -> None`
Replaces occurrences of a keyword in the specified column of the messages.

Parameters:
- `keyword` (str): The keyword to replace.
- `replacement` (str): The replacement string.
- `column` (str): The column to search for the keyword (default: "content").
- `case_sensitive` (bool): Whether the keyword search should be case-sensitive (default: False).

##### `search_keywords`
`(self, keywords: str | list[str], case_sensitive: bool = False, reset_index: bool = False, dropna: bool = False) -> dataframe.ln_DataFrame`
Searches for keywords in the messages and returns a new DataFrame with matching messages.

Parameters:
- `keywords` (`str | list[str]`): The keyword(s) to search for.
- `case_sensitive` (bool): Whether the keyword search should be case-sensitive (default: False).
- `reset_index` (bool): Whether to reset the index of the resulting DataFrame (default: False).
- `dropna` (bool): Whether to drop rows with missing values (default: False).

Returns:
`dataframe.ln_DataFrame`: A new DataFrame containing the messages that match the specified keywords.

##### `extend`
`(self, messages: dataframe.ln_DataFrame, **kwargs) -> None`
Extends the branch with additional messages.

Parameters:
- `messages` (`dataframe.ln_DataFrame`): The DataFrame containing the messages to add.
- `**kwargs`: Additional keyword arguments.

##### `filter_by`
`(self, role: str | None = None, sender: str | None = None, start_time=None, end_time=None, content_keywords: str | list[str] | None = None, case_sensitive: bool = False) -> dataframe.ln_DataFrame`
Filters the messages based on specified criteria.

Parameters:
- `role` (`str | None`): The role to filter by (default: None).
- `sender` (`str | None`): The sender to filter by (default: None).
- `start_time` (Any): The start time to filter by (default: None).
- `end_time` (Any): The end time to filter by (default: None).
- `content_keywords` (`str | list[str] | None`): The keyword(s) to search for in the content (default: None).
- `case_sensitive` (bool): Whether the keyword search should be case-sensitive (default: False).

Returns:
`dataframe.ln_DataFrame`: A new DataFrame containing the filtered messages.


##### `from_csv`
`(cls, **kwargs) -> "BaseBranch"`
Creates a `BaseBranch` instance from a CSV file.

Parameters:
- `**kwargs`: Keyword arguments for reading the CSV file.

Returns:
BaseBranch: A new `BaseBranch` instance created from the CSV file.

##### `from_json_string`
`(cls, **kwargs) -> "BaseBranch"`
Creates a `BaseBranch` instance from a JSON string.

Parameters:
- `**kwargs`: Keyword arguments for parsing the JSON string.

Returns:
BaseBranch: A new `BaseBranch` instance created from the JSON string.


##### `to_csv_file`
`(self, filename: PATH_TYPE = "messages.csv", dir_exist_ok: bool = True, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, **kwargs) -> None`
Exports the branch messages to a CSV file.

Parameters:
- `filename` (`PATH_TYPE`): Destination path for the CSV file (default: `"messages.csv"`).
- `dir_exist_ok` (`bool`): If False, an error is raised if the directory exists (default: `True`).
- `timestamp` (`bool`): If True, appends a timestamp to the filename (default: True).
- `time_prefix` (`bool`): If True, prefixes the filename with a timestamp (default: `False`).
- `verbose` (`bool`): If True, prints a message upon successful export (default: `True`).
- `clear` (`bool`): If True, clears the messages after exporting (default: `True`).
- `**kwargs`: Additional keyword arguments for `pandas.DataFrame.to_csv()`.

##### `to_json_file`
`(self, filename: PATH_TYPE = "messages.json", dir_exist_ok: bool = True, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, **kwargs) -> None`
Exports the branch messages to a JSON file.

Parameters:
- `filename` (`PATH_TYPE`): Destination path for the JSON file (default: "messages.json").
- `dir_exist_ok` (bool): If False, an error is raised if the directory exists (default: True).
- `timestamp` (bool): If True, appends a timestamp to the filename (default: True).
- `time_prefix` (bool): If True, prefixes the filename with a timestamp (default: False).
- `verbose` (bool): If True, prints a message upon successful export (default: True).
- `clear` (bool): If True, clears the messages after exporting (default: True).
- `**kwargs`: Additional keyword arguments for `pandas.DataFrame.to_json()`.

##### `log_to_csv`
`(self, filename: PATH_TYPE = "log.csv", dir_exist_ok: bool = True, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, flatten_=True, sep="[^_^]", **kwargs) -> None`
Exports the data logger contents to a CSV file.

Parameters:
- `filename` (PATH_TYPE): Destination path for the CSV file (default: `"log.csv"`).
- `dir_exist_ok` (bool): If False, an error is raised if the directory exists (default: True).
- `timestamp` (bool): If True, appends a timestamp to the filename (default: True).
- `time_prefix` (bool): If True, prefixes the filename with a timestamp (default: False).
- `verbose` (bool): If True, prints a message upon successful export (default: True).
- `clear` (bool): If True, clears the logger after exporting (default: True).
- `flatten_` (bool): If True, flattens the log data (default: True).
- `sep` (str): The separator used for flattening the log data (default:` "[^_^]"`).
- `**kwargs`: Additional keyword arguments for `pandas.DataFrame.to_csv()`.

##### `log_to_json`
`(self, filename: PATH_TYPE = "log.json", dir_exist_ok: bool = True, timestamp: bool = True, time_prefix: bool = False, verbose: bool = True, clear: bool = True, flatten_=True, sep="[^_^]", **kwargs) -> None`
Exports the data logger contents to a JSON file.

Parameters:
- `filename` (`PATH_TYPE`): Destination path for the JSON file (default: `"log.json"`).
- `dir_exist_ok` (`bool`): If False, an error is raised if the directory exists (default: `True`).
- `timestamp` (`bool`): If True, appends a [[System Utility Lib#^bfa89d|timestamp]] to the filename (default: `True`).
- `time_prefix` (`bool`): If True, prefixes the filename with a timestamp (default: False).
- `verbose` (`bool`): If True, prints a message upon successful export (default: `True`).
- `clear` (`bool`): If True, clears the logger after exporting (default: `True`).
- `flatten_` (`bool`): If True, [[Nested Data Lib#^3073e9|flatten]] the log data (default: `True`).
- `sep` (`str`): The separator used for flattening the log data (default: `"[^_^]"`).
- `**kwargs`: Additional keyword arguments for `pandas.DataFrame.to_json()`.

##### `load_log`
`(self, filename, flattened=True, sep="[^_^]", verbose=True, **kwargs) -> None`
Loads log data from a file into the data logger.

Parameters:
- `filename` (str): The path to the log file.
- `flattened` (bool): Whether the log data is flattened (default: True).
- `sep` (str): The separator used for flattening the log data (default: `"[^_^]"`).
- `verbose` (bool): If True, prints a message upon successful loading (default: True).
- `**kwargs`: Additional keyword arguments for reading the log file.
