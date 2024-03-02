

# Session Class API Reference

Manages multiple conversation branches within a conversational system, offering functionalities for branch management, message aggregation, logging, and session data persistence.

### Overview

The `Session` class serves as a container for managing multiple `Branch` instances within a conversational AI system. It provides mechanisms for creating new conversation branches, aggregating messages across branches, logging session activities, and maintaining a central configuration for interacting with language learning models (LLMs).

### Attributes

- `branches` _(Dict[str, Branch])_: Maps branch names to their respective `Branch` instances.
- `default_branch` _([[Branch]])_: The branch designated as the default for the session.
- `datalogger` _(DataLogger)_: Logs session activities and interactions.
- `mail_manager` _([[Mail Manager]])_: Manages mail exchanges across branches.
- `llmconfig` _(Dict)_: Configuration settings for the LLM service used by the default branch.

### Constructor

```python
def __init__(self, system=None, default_branch=None, default_branch_name=None, sender=None, llmconfig=None, service=None, branches=None, actions=None, instruction_sets=None, action_manager=None, messages=None, datalogger=None, persist_path=None, **kwargs):
```

Initializes a new `Session` instance, setting up default configurations for managing conversation branches.

#### Parameters

- `system` _(System | str | Dict[str, Any] | None)_: Initial system message or configuration for the default branch.
- `default_branch` _(Branch | None)_: Pre-existing `Branch` instance to set as the default.
- `default_branch_name` _(str | None)_: Name of the default branch. Used if initializing a new default branch.
- `sender` _(str | None)_: Default sender for system messages in the default branch.
- `llmconfig` _(Dict | None)_: LLM service configuration for the default branch.
- `service` _(Any)_: LLM service instance for natural language processing.
- `branches` _(Dict[str, Branch] | None)_: Existing branches to include in the session.
- `actions` _(BaseActionNode | List[BaseActionNode] | None)_: Actions to register with the default branch.
- `instruction_sets` _(Dict | None)_: Instruction sets for structured interactions.
- `action_manager` _(ActionManager | None)_: Manages actions within the default branch.
- `messages` _(DataFrame | None)_: Preloaded conversation messages for the default branch.
- `datalogger` _(DataLogger | None)_: Logger for session activities.
- `persist_path` _(str | None)_: Path for persisting session data.
- `**kwargs` _(Any)_: Additional keyword arguments for branch setup.

### Methods

The `Session` class includes methods for managing branches (`new_branch`, `get_branch`, `delete_branch`, `merge_branch`), interacting with conversations (`chat`, `ReAct`, `auto_followup`), and handling session data (`all_messages`, `log_to_csv`, `to_json`).

### Examples

```python
# Initialize a session with a default branch and logging path
session = Session(default_branch_name='main', persist_path='/logs/')

# Create a new branch
session.new_branch('Support', system='Welcome to Support Branch')

# Aggregate and log messages
all_messages = session.all_messages()
session.log_to_csv('all_messages.csv')
```

This class streamlines the creation and management of conversation branches, facilitates message logging and data persistence, and supports dynamic interaction with LLMs.

### `all_messages` Method

Aggregates all messages from each branch into a single pandas DataFrame.

#### Returns

- `DataFrame`: A unified view of all messages across the session's branches.

### `all_responses` Method

Compiles all responses from assistants across branches into a single DataFrame.

#### Returns

- `DataFrame`: Consolidates all assistant responses for analysis and reporting.

### `all_assistant_responses` Method

Collects all assistant-generated responses from each branch.

#### Returns

- `DataFrame`: A centralized dataset of all assistant responses across the session.

### `all_action_responses` Method

Aggregates all action responses from each branch into one DataFrame.

#### Returns

- `DataFrame`: Offers insights into the outcomes of actions taken across the session.

### `all_action_requests` Method

Compiles all action requests from each branch into a single DataFrame.

#### Returns

- `DataFrame`: Provides a comprehensive overview of requested actions across the session.

### `all_messages` Method

Aggregates all messages from each branch into a single DataFrame, providing an overview of the conversation across the session.

#### Returns

- `DataFrame`: A pandas DataFrame containing all messages from the session's branches, structured according to the message schema defined in the Branch class.

#### Example

```python
all_msgs = session.all_messages
print(all_msgs.head())
```

### `all_responses` Method

Aggregates all responses from assistants across branches into a DataFrame, useful for analyzing conversational outcomes.

#### Returns

- `DataFrame`: A pandas DataFrame consolidating all assistant responses from the session's branches, formatted to align with the response schema used in Branch instances.

#### Example

```python
all_responses = session.all_responses
print(all_responses.head())
```

### `all_assistant_responses` Method

Collects all assistant-generated responses from each branch, combining them into a single DataFrame for a centralized view of system interactions.

#### Returns

- `DataFrame`: A pandas DataFrame containing all assistant-generated responses from all branches, adhering to the assistant response schema defined in Branch instances.

#### Example

```python
assistant_responses = session.all_assistant_responses
print(assistant_responses.head())
```

### `all_action_responses` Method

Aggregates all action responses from each branch into a single DataFrame, offering insights into the outcomes of actions taken across the session.

#### Returns

- `DataFrame`: A pandas DataFrame that consolidates all action responses from the session's branches, formatted according to the action response schema outlined in Branch instances.

#### Example

```python
all_action_responses = session.all_action_responses
print(all_action_responses.head())
```

### `all_action_requests` Method

Compiles all action requests from each branch into a single DataFrame, providing a comprehensive overview of requested actions across the session.

#### Returns

- `DataFrame`: A pandas DataFrame containing all action requests across the session's branches, adhering to the schema for action requests defined in Branch instances.

#### Example

```python
all_action_requests = session.all_action_requests
print(all_action_requests.head())
```

### `info` Method

Summarizes session information by aggregating key metrics and details from each branch, returning a dictionary with branch names as keys and their info dictionaries as values.

#### Returns

- `Dict[str, Any]`: A dictionary mapping each branch name to its corresponding info dictionary, which includes metrics and details specific to that branch.

#### Example

```python
session_info = session.info
for branch_name, branch_info in session_info.items():
    print(f"{branch_name}: {branch_info}")
```

### `sender_info` Method

Provides a summary of sender-specific information from each branch, aggregating metrics and details related to message senders across the session.

#### Returns

- `Dict[str, Any]`: A dictionary where each key is a branch name, and its value is another dictionary containing sender-specific metrics for that branch.

#### Example

```python
sender_info = session.sender_info
for branch_name, info in sender_info.items():
    print(f"{branch_name}: {info}")
```

### `default_branch_name` Property

Retrieves the name of the session's default branch. This property offers a simple way to identify the current default branch within the session.

#### Returns

- `str`: The name of the default branch.

#### Example

```python
print(session.default_branch_name)
```

### `concat_logs` Method

Consolidates logs from all branches into the session's datalogger, preparing them for unified export or analysis.

#### Example

```python
session.concat_logs()
```

This method aggregates log entries recorded in each branch's individual datalogger, ensuring a comprehensive logging of session activities.

### `log_to_csv` Method

Exports the consolidated session logs to a CSV file, with options for timestamping and versioning of log files.

#### Parameters

- `filename` _(str)_: Name or path of the CSV file for export. Default is 'log.csv'.
- `file_exist_ok` _(bool)_: If False, an error is raised if the file already exists. Default is False.
- `timestamp` _(bool)_: If True, appends a timestamp to ensure filename uniqueness. Default is True.
- `time_prefix` _(bool)_: If True, prefixes the filename with a timestamp. Default is False.
- `verbose` _(bool)_: If True, prints a confirmation message upon export. Default is True.
- `clear` _(bool)_: If True, clears the datalogger after exporting. Default is True.
- `**kwargs`_: Additional keyword arguments for `DataFrame.to_csv`.

#### Example

```python
session.log_to_csv('session_logs.csv')
```

### `log_to_json` Method

Exports session logs to a JSON file, consolidating logs for easy sharing and analysis.

#### Parameters

Same as `log_to_csv`, but for exporting to a JSON format.

#### Example

```python
session.log_to_json('session_logs.json')
```

### `from_csv` Method

Initializes a Session instance from conversation data stored in a CSV file, creating a default branch with the imported data.

#### Parameters

- `filepath` _(str)_: Path to the CSV file containing conversation data.
- Additional parameters similar to the constructor for initializing the session and default branch.

#### Returns

- `Session`: An initialized Session instance with a default branch loaded from the CSV file.

#### Example

```python
session = Session.from_csv('data/conversations.csv', default_branch_name='Support')
```

This method streamlines the process of loading conversation data into a session from a CSV file, facilitating quick setup and integration.

### `from_json` Method

Initializes a Session instance from conversation data stored in a JSON file, creating a default branch with the imported data.

#### Parameters

- `filepath` _(str)_: Path to the JSON file containing conversation data.
- Additional parameters similar to the constructor for initializing the session and default branch.

#### Returns

- `Session`: An initialized Session instance with a default branch configured with the JSON file data.

#### Example

```python
session = Session.from_json_string('data/conversations.json',
                                   default_branch_name='CustomerService')
```

### `to_csv` Method

Exports conversation data to a CSV file, with options to target a specific branch or all branches for the export.

#### Parameters

- `filepath` _(str | None)_: Path to the CSV file where data will be exported. If not provided, a default naming scheme is used.
- `branch` _(str | Branch)_: Specifies the branch to export. Use 'all' to export data from all branches. Default is 'all'.
- Additional parameters for customization of the export process.

#### Example

```python
session.to_csv(filepath='all_conversations.csv', branch='all')
```

### `to_json` Method

Exports conversation data to a JSON file, targeting either a specific branch or all branches within the session.

#### Parameters

Similar to `to_csv`, but for exporting to a JSON format.

#### Example

```python
session.to_json(filepath='conversation_data.json', branch='CustomerInquiries')
```

These methods facilitate the export of conversation data from the session, providing flexibility in data sharing and analysis.

### `from_json` Method

Initializes a Session instance from conversation data stored in a JSON file, creating a default branch with the imported data and configurations.

#### Parameters

- `filepath` _(str)_: Path to the JSON file containing conversation data.
- Additional parameters similar to `from_csv` for initializing the session and default branch.

#### Returns

- `Session`: A new Session instance with a default branch configured with the data from the JSON file.

#### Example

```python
session = Session.from_json_string('data/conversations.json',
                                   default_branch_name='CustomerService')
```

### `to_csv` Method

Exports conversation data to a CSV file, targeting either a specific branch or all branches within the session.

#### Parameters

- `filepath` _(str | None)_: Path or name of the CSV file to export data to. Defaults to a generated name based on branch and timestamp.
- `branch` _(str | Branch | 'all')_: Specifies the branch to export. Defaults to 'all' for exporting from all branches.
- Additional parameters for customizing the export process, similar to `log_to_csv`.

#### Example

```python
session.to_csv(filepath='all_conversations.csv', branch='all')
```

### `to_json` Method

Exports conversation data to a JSON file, offering a structured format for conversation data across specified branches or the entire session.

#### Parameters

Same as `to_csv`, but for exporting to a JSON format.

#### Example

```python
session.to_json(filepath='conversation_data.json', branch='CustomerInquiries')
```

These methods provide flexible options for exporting conversation data from the session, facilitating integration, sharing, and further processing.

### `register_actions` Method

Registers one or more actions with the action manager of the default branch, enhancing the conversation capabilities.

#### Parameters

- `actions` _(Union[BaseActionNode, List[BaseActionNode]])_: A single action or a list of actions to be registered with the default branch's action manager.

#### Example

```python
session.register_actions([new_action])
```

This method allows for the dynamic addition of actions to the session, facilitating enhanced conversational interactions.

### `new_branch` Method

Creates and adds a new conversation branch to the session with specified configurations.

#### Parameters

- `branch_name` _(str | None)_: Name of the new branch. Must be unique across the session.
- Additional parameters for configuring the new branch, similar to those provided in the session constructor.

#### Example

```python
session.new_branch('Support', system='Welcome to Support Branch')
```

This method enables the session to manage diverse conversation flows by adding specialized branches.

### `get_branch` Method

Retrieves a branch from the session based on its name or direct reference, offering flexibility in accessing branches.

#### Parameters

- `branch` _(str | Branch | None)_: The name of the branch or the Branch instance to retrieve. Defaults to the default branch if None.
- `get_name` _(bool)_: If True, returns a tuple of (Branch instance, branch name).

#### Returns

- `Branch` or `tuple[Branch, str]`: The requested Branch instance, or a tuple of the Branch instance and its name if `get_name` is True.

#### Example

```python
my_branch = session.get_branch('CustomerService')
```

### `change_default_branch` Method

Sets a new branch as the default for the session, facilitating shifts in conversational focus or operational context.

#### Parameters

- `branch` _(str | Branch)_: The name of the branch or the Branch instance to set as the new default.

#### Example

```python
session.change_default_branch('AfterSalesSupport')
```

This operation dynamically changes the session's focal point to another existing branch, enhancing session flexibility.

### `delete_branch` Method

Removes a specified branch from the session, effectively deleting its configuration, messages, and actions.

#### Parameters

- `branch` _(str | Branch)_: The name of the branch or the Branch instance to delete.
- `verbose` _(bool)_: If True, prints a confirmation message upon successful deletion.

#### Returns

- `bool`: True if the branch was successfully deleted, False otherwise.

#### Example

```python
session.delete_branch("TemporaryBranch")
```

### `merge_branch` Method

Merges data and configurations from one branch into another, streamlining session management by consolidating conversational data.

#### Parameters

- `from_branch` _(str | Branch)_: The source branch to merge from.
- `to_branch` _(str | Branch)_: The target branch to merge into.
- `update` _(bool)_: If True, updates existing entries in the target branch. Defaults to True.
- `del_` _(bool)_: If True, deletes the source branch after merging. Defaults to False.

#### Example

```python
session.merge_branch("TemporaryConversations", "MainConversations", del_=True)
```

### `collect` Method

Initiates the collection of messages from specified branches, preparing them for sending, aggregation, or analysis.

#### Parameters

- `sender` _(str | Branch | list[str] | list[Branch] | None)_: The branch(es) from which to collect messages. Defaults to all branches if None.

#### Example

```python
session.collect("CustomerService")
```

### `send` Method

Dispatches collected messages to their intended recipients from specified branches, ensuring message delivery across the session.

#### Parameters

- `recipient` _(str | Branch | list[str] | list[Branch] | None)_: The branch(es) whose messages are to be sent. Defaults to all branches if None.

#### Example

```python
session.send("CustomerFeedback")
```

These methods provide flexible options for managing branches within the session, facilitating targeted message delivery and efficient message management.

### `collect_send_all` Method

Performs a complete cycle of collecting and sending messages across all branches within the session, optionally processing all pending incoming messages.

#### Parameters

- `receive_all` _(bool)_: If True, processes all pending incoming messages after collecting and sending, completing the communication cycle.

#### Example

```python
session.collect_send_all(receive_all=True)
```

This method ensures a synchronized state across all conversation branches, enhancing session coherence and interaction capabilities.

### `setup_default_branch` Method

Configures the default branch with provided parameters. Primarily for internal use, it allows for the reconfiguration of the default branch's settings.

#### Parameters

- `**kwargs`: Keyword arguments corresponding to the Branch class's initialization parameters.

#### Example

```python
session.setup_default_branch(system="Updated system message")
```

### `chat` Method

Conducts an asynchronous chat exchange in a specified branch or the default branch, processing instructions and optionally invoking actions.

#### Parameters

- `instruction` _(Union[Instruction, str])_: The chat instruction, either as a string or an Instruction object.
- `context` _(Optional[Any])_: Optional context for enriching the chat conversation.
- `sender` _(Optional[str])_: Identifier for the sender of the chat message.
- `system` _(Optional[Union[System, str, Dict[str, Any]])_: System message or configuration for the chat.
- `actions` _(Union[bool, BaseActionNode, List[BaseActionNode], str, List[str]])_: Specifies actions to invoke as part of the chat.
- `out` _(bool)_: If True, outputs the chat instruction as a system message.
- `invoke` _(bool)_: If True, invokes the specified actions.
- `branch` _(Branch | str | None)_: The branch in which to conduct the chat. Defaults to the default branch if None.
- `**kwargs`: Additional keyword arguments for model calling or action invocation.

#### Example

```python
await session.chat("How can I assist you today?", branch="CustomerService")
```

This method facilitates dynamic interaction within the session, allowing for tailored conversation management and specialized interactions in any branch.

### `ReAct` Method

Performs a reason-action cycle with optional actions invocation over multiple rounds, simulating decision-making processes based on initial instructions and available actions.

#### Parameters

- `instruction` _(Union[Instruction, str])_: Initial instruction for the cycle.
- `context` _(Optional[Any])_: Context relevant to the instruction, enhancing the reasoning process.
- `sender` _(Optional[str])_: Identifier for the message sender, enriching the conversational context.
- `system` _(Optional[Union[System, str, Dict[str, Any]])_: Initial system message or configuration for the chat session.
- `actions` _(Union[bool, BaseActionNode, List[BaseActionNode], str, List[str]])_: Tools to be invoked during the reason-action cycle.
- `num_rounds` _(int)_: Number of reason-action cycles to perform.
- `branch` _(Branch | str | None)_: The branch in which to perform the ReAct cycle. Defaults to the default branch if None.
- `**kwargs`: Additional keyword arguments for customization and actions invocation.

#### Example

```python
await session.ReAct("Analyze user feedback", num_rounds=2, branch="AnalysisBranch")
```

### `auto_followup` Method

Automatically generates follow-up actions based on previous chat interactions and actions invocations, facilitating extended conversation flows.

#### Parameters

- `instruction` _(Union[Instruction, str])_: The initial instruction for follow-up.
- `context` _(Optional[Any])_: Context relevant to the instruction, supporting the follow-up process.
- `sender` _(Optional[str])_: Identifier for the message sender, adding context to the follow-up.
- `system` _(Optional[Union[System, str, Dict[str, Any]])_: Initial system message or configuration for the session.
- `actions` _(Union[bool, BaseActionNode, List[BaseActionNode], str, List[str], List[Dict]])_: Specifies actions to consider for follow-up.
- `max_followup` _(int)_: Maximum number of follow-up chats allowed.
- `out` _(bool)_: If True, outputs the result of the follow-up action.
- `branch` _(Branch | str | None)_: The branch in which to conduct the follow-up. Defaults to the default branch if None.
- `**kwargs`: Additional keyword arguments for follow-up customization.

#### Example

```python
await session.auto_followup("Finalize report", max_followup=2, branch="ReportBranch")
```

These methods enable dynamic and automated decision-making within conversations, supporting complex interaction patterns and action-driven dialogues.
