
This module contains the `Branch` class, which represents a branch in a conversation tree.

### Class: `Branch`
parent: [[base branch]], [[branch flow]]

A class representing a branch in a conversation tree.

#### Attributes:
- `sender` (str): The sender of the branch (default: "system").
- `tool_manager` ([[tool manager|ToolManager]]): The tool manager for the branch.
- `service` ([[LLM Service#^0916ce|BaseService]]): The service associated with the branch.
- `llmconfig` (dict): The configuration for the language model.
- `status_tracker` ([[LLM Service#^deb0a1|StatusTracker]]): The status tracker for the branch.
- `pending_ins` (dict): The pending incoming mails for the branch.
- `pending_outs` (`deque`): The pending outgoing mails for the branch.

#### Methods:
##### `__init__`
`(self, name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, **kwargs) -> None`
Initializes the `Branch` instance.

Parameters:
- `name` (str | None): The name of the branch (optional).
- `system` (dict | list | System | None): The [[messages#^9d4814|system]] message for the branch (optional).
- `messages` (`pd.DataFrame` | None): The messages in the branch (optional).
- `service` (BaseService | None): The service associated with the branch (optional).
- `sender` (str | None): The sender of the branch (optional, default: "system").
- `llmconfig` (`dict[str, str | int | dict] | None`): The configuration for the language model (optional).
- `tools` (`list[Callable | Tool] | None`): The [[tool]] to register in the branch (optional).
- `datalogger` (DataLogger | None): The [[data logger]] for the branch (optional).
- `persist_path` (PATH_TYPE | None): The path to persist the branch data (optional).
- `tool_manager` (ToolManager | None): The[[ tool manager]] for the branch (optional).
- `**kwargs`: Additional keyword arguments.

Raises:
- `TypeError`: If there is an error in registering the tools.

##### `from_csv`
`(cls, filepath, name=None, service=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, read_kwargs=None, **kwargs) -> Branch`
Creates a `Branch` instance from a CSV file.

Parameters:
- `filepath` (str): The path to the CSV file.
- `name` (str | None): The name of the branch (optional).
- `service` (BaseService | None): The service associated with the branch (optional).
- `llmconfig` (dict[str, str | int | dict] | None): The configuration for the language model (optional).
- `tools` (TOOL_TYPE | None): The tools to register in the branch (optional).
- `datalogger` (DataLogger | None): The data logger for the branch (optional).
- `persist_path` (PATH_TYPE | None): The path to persist the branch data (optional).
- `tool_manager` (ToolManager | None): The tool manager for the branch (optional).
- `read_kwargs` (dict | None): Additional keyword arguments for reading the CSV file (optional).
- `**kwargs`: Additional keyword arguments.

Returns:
`Branch`: The created `Branch` instance.

##### `from_json_string`
`(cls, filepath, name=None, service=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, read_kwargs=None, **kwargs) -> Branch`
Creates a `Branch` instance from a JSON string file.

Parameters:
- `filepath` (str): The path to the JSON string file.
- `name` (str | None): The name of the branch (optional).
- `service` (BaseService | None): The service associated with the branch (optional).
- `llmconfig` (dict[str, str | int | dict] | None): The configuration for the language model (optional).
- `tools` (TOOL_TYPE | None): The tools to register in the branch (optional).
- `datalogger` (DataLogger | None): The data logger for the branch (optional).
- `persist_path` (PATH_TYPE | None): The path to persist the branch data (optional).
- `tool_manager` (ToolManager | None): The tool manager for the branch (optional).
- `read_kwargs` (dict | None): Additional keyword arguments for reading the JSON string file (optional).
- `**kwargs`: Additional keyword arguments.

Returns:
`Branch`: The created `Branch` instance.

##### `messages_describe`
`(self) -> dict[str, Any]`
Describes the messages in the branch.

Returns:
`dict[str, Any]`: A dictionary describing the messages in the branch.

##### `merge_branch`
`(self, branch: Branch, update=True) -> None`
Merges another branch into the current branch.

Parameters:
- `branch` (Branch): The branch to merge.
- `update` (bool): Whether to update the existing attributes or add new ones (default: True).

##### `register_tools`
`(self, tools: Union[Tool, list[Tool | Callable], Callable]) -> None`
Registers tools in the branch's tool manager.

Parameters:
- `tools` (`Union[Tool, list[Tool | Callable], Callable]`): The tool(s) to register.

##### `delete_tools`
`(self, tools: Union[T, list[T], str, list[str]], verbose=True) -> bool`
Deletes tools from the branch's tool manager.

Parameters:
- `tools` (`Union[T, list[T], str, list[str]]`): The tool(s) to delete.
- `verbose` (`bool`): Whether to print success/failure messages (default: True).

Returns:
`bool`: True if the tools were successfully deleted, False otherwise.

##### `send`
`(self, recipient: str, category: str, package: Any) -> None`
Sends a mail to a recipient.

Parameters:
- `recipient` (str): The recipient of the mail.
- `category` (str): The category of the mail.
- `package` (Any): The package to send in the mail.

##### `receive`
`(self, sender: str, messages=True, tools=True, service=True, llmconfig=True) -> None`
Receives mails from a sender and updates the branch accordingly.

Parameters:
- `sender` (str): The sender of the mails.
- `messages` (bool): Whether to receive message updates (default: True).
- `tools` (bool): Whether to receive tool updates (default: True).
- `service` (bool): Whether to receive service updates (default: True).
- `llmconfig` (bool): Whether to receive language model configuration updates (default: True).

Raises:
- `ValueError`: If there are no packages from the specified sender, or if the received data formats are invalid.

##### `receive_all`
`(self) -> None`
Receives all pending mails and updates the branch accordingly.

#### Properties:
- `has_tools` (bool): Checks if the branch has any registered tools.
