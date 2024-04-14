## MonoFollowup Class
A specialized class designed for managing follow-up chat conversations with an LLM. This class extends `MonoChat`, providing capabilities to handle additional interactions based on user or system input, and to utilize various tools during the conversation.

### Attributes
- **FOLLOWUP_PROMPT (str)**: Default prompt template used for follow-up interactions. Informs the user about the remaining number of follow-ups and guides on subsequent actions.
- **OUTPUT_PROMPT (str)**: Default prompt for presenting the final output to the user, detailing the original instructions provided.

### Methods

#### `__init__`
Initializes the `MonoFollowup` instance with a specific branch.
- **Parameters**:
  - `branch`: The `Branch` instance associated with the follow-up operations.
- **Returns**:
  - None

#### `followup`
Conducts a sequence of follow-up chats with an LLM based on provided instructions, optionally using various tools.
- **Parameters**:
  - `instruction (Instruction | str | dict)`: Detailed instructions for the follow-up chat.
  - `context (Optional[Any])`: Additional context to be considered during the chat.
  - `sender (Optional[str])`: Identifier for the sender of the message.
  - `system (Optional[Any])`: System message to process.
  - `tools (Optional[Any])`: Specifies the tools to be invoked during the chat.
  - `max_followup (int)`: Maximum number of follow-up interactions allowed.
  - `followup_prompt (Optional[str])`: Custom prompt for follow-up chats.
  - `output_prompt (Optional[str])`: Custom prompt for presenting the final output.
  - `**kwargs`: Additional keyword arguments for the chat configuration.
- **Returns**:
  - `str`: The result of the follow-up chat.

#### `_get_prompt`
Generates the appropriate prompt for a follow-up chat based on provided parameters.
- **Parameters**:
  - `prompt (Optional[str])`: Specific prompt for the follow-up.
  - `default (Optional[str])`: Default prompt if no specific prompt is provided.
  - `num_followup (Optional[int])`: Remaining number of follow-ups allowed.
  - `instruction (Optional[Any])`: Original instructions provided by the user.
- **Returns**:
  - `str`: The generated prompt for the follow-up chat.

#### `_create_followup_config`
Creates configuration settings for the follow-up chat, considering the provided tools and parameters.
- **Parameters**:
  - `tools (Optional[Any])`: Tools to be invoked during the chat.
  - `tool_choice (str)`: Strategy for tool selection ("auto" by default).
  - `**kwargs`: Additional configuration settings.
- **Returns**:
  - `dict`: Configuration for the follow-up chat.
- **Raises**:
  - `ValueError`: If no tools are registered or found.

#### `_followup`
Executes the actual follow-up chat interactions, managing the sequence based on user inputs and system configurations.
- **Parameters**:
  - Same as `followup` method.
- **Returns**:
  - `Optional[str]`: The result of the follow-up chat, depending on the 'out' flag.

### Usage Example
```python
# Assuming 'branch' is a pre-configured Branch instance
mono_followup = MonoFollowup(branch)
result = await mono_followup.followup(
    instruction="Further details on user preferences?",
    max_followup=3,
    tools=True,
    out=True,
    invoke=True
)
