## `MonoChatMixin` Class
A `mixin` class that combines functionalities from `MonoChatConfigMixin` and `MonoChatInvokeMixin` to manage chatbot interactions comprehensively.

### `MonoChatConfigMixin`
`Mixin` class for configuring chatbots.

#### Methods

##### _create_chat_config
Creates a chat configuration based on the provided parameters.
- **Parameters**:
  - `instruction (Instruction | str | dict[str, Any])`: Instruction for the chatbot.
  - `context (Any)`: Context for the chatbot.
  - `sender (str)`: Sender of the message.
  - `system (str | dict[str, Any])`: System message for the chatbot.
  - `output_fields`: Output fields for the chatbot.
  - `form`: Prompt template for the chatbot.
  - `tools (TOOL_TYPE)`: Tools for the chatbot.
  - `**kwargs`: Additional keyword arguments.
- **Returns**:
  - `Any`: The chat configuration.

### `MonoChatInvokeMixin`
`Mixin` class for invoking chatbots.

#### Methods

##### `_output`
Processes the output of the chatbot.
- **Parameters**:
  - `invoke`: Flag to invoke the tools.
  - `out`: Flag to return the output.
  - `output_fields`: Output fields for the chatbot.
  - `func_calls_`: Function calls for invoking the tools.
  - `form`: Prompt template.
  - `return_template (bool)`: Flag to return the prompt template.
- **Returns**:
  - `Any`: The processed output or the form template.

##### `_return_response`
Returns the response from the chatbot based on the last message content.
- **Parameters**:
  - `content_`: Content of the last message.
  - `output_fields`: Output fields for the chatbot.
- **Returns**:
  - `Any`: The response from the chatbot.

##### `_invoke_tools`
Invokes the tools associated with the chatbot.
- **Parameters**:
  - `content_`: Content of the last message.
  - `func_calls_`: Function calls for invoking the tools.
- **Returns**:
  - `list`: Results of invoking the tools.

##### `_process_chatcompletion`
Processes the chat completion.
- **Parameters**:
  - `payload`: Payload for the chat completion.
  - `completion`: Completed chat response.
  - `sender`: Sender of the message.

##### `_call_chatcompletion`
Calls the chat completion API.
- **Parameters**:
  - `sender`: Sender of the message.
  - `with_sender (bool)`: Include the sender in the chat messages.
  - `**kwargs`: Additional keyword arguments for the chat completion API.


## MonoChat Class
A specialized class for handling chat conversations with an LLM, capable of processing instructions, system messages, and optionally invoking tools. This class extends `BaseMonoFlow` and incorporates the `MonoChatMixin` to leverage a broad range of chat functionalities.

### Attributes
- **branch**: The `Branch` instance associated with the chat, used to perform all chat operations.

### Methods

#### __init__
Initializes the `MonoChat` instance with a specified branch.
- **Parameters**:
  - `branch`: The `Branch` instance to perform chat operations.
- **Returns**:
  - None

#### chat
Conducts a chat conversation with an LLM, processing provided instructions and system messages, and optionally invoking tools if specified.
- **Parameters**:
  - `instruction (Optional[Union[Instruction, str]])`: Instruction for the chatbot; can be an `Instruction` object or a string.
  - `context (Optional[Any])`: Additional context information for the chat session.
  - `sender (Optional[str])`: Identifier for the sender of the chat message.
  - `system (Optional[Union[System, str, dict[str, Any]])`: System message to process during the chat.
  - `tools (Optional[Union[bool, Tool, List[Tool], str, List[str]])`: Specifies whether and which tools to invoke during the chat.
  - `out (bool)`: If set to `True`, the chat response will be outputted.
  - `invoke (bool)`: If set to `True`, any specified tools will be invoked as part of the chat session.
  - `output_fields (Optional[Any])`: Specifies the fields to include in the output of the chat.
  - `form (Optional[Any])`: The prompt template for structuring the chat inputs and outputs.
  - `**kwargs`: Arbitrary keyword arguments for enhancing chat configurations and functionalities.
- **Returns**:
  - `Any`: The result of the chat conversation, depending on the `out` parameter and other configurations.

### Usage Example
```python
# Assuming 'branch' is a pre-configured Branch instance
mono_chat = MonoChat(branch)
result = await mono_chat.chat(
    instruction="Ask about user preferences",
    system={"message": "System initialization"},
    tools=True,
    out=True,
    invoke=True
)
