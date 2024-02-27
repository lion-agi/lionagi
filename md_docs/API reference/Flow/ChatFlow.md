
## ChatFlow Objects

`ChatFlow` class facilitates asynchronous communication and interaction flows within a chat environment, leveraging Language Learning Models (LLMs) and custom actions for dynamic conversation management. It provides static methods for handling chat completions, executing chat-based instructions, and managing reason-action cycles with optional BaseActionNode invocation.

### Methods

- **call_chatcompletion**: Asynchronously calls the chat completion provider with the current message queue, integrating LLM services for response generation. Supports inclusion of sender information and customization of tokenizer parameters.

- **chat**: Conducts a chat session by processing instructions and optionally invoking actions based on the chat content. Allows for a flexible integration of system messages, context, and sender details to tailor the chat flow.

- **ReAct**: Performs a reason-action cycle, allowing for multiple rounds of reasoning and action planning based on the initial instructions and available actions. Supports BaseActionNode invocation to enhance the decision-making process.

- **auto_followup**: Automatically generates follow-up actions based on previous chat interactions and BaseActionNode outputs. Facilitates extended conversation flows by iterating through additional reasoning and action steps as needed.


```python
@staticmethod
async def call_chatcompletion(
	branch: 'Branch', sender: str | None = None,
    with_sender: bool = False, tokenizer_kwargs: dict = {},
    **kwargs) -> None:
    """Asynchronously calls the chat completion service with the current message queue."""
```

- **Args**:
  - `branch`: The [[Branch]] instance calling the service.
  - `sender`: The name of the sender to include in chat completions (optional).
  - `with_sender`: If True, includes sender information in messages.
  - `tokenizer_kwargs`: Keyword arguments for the tokenizer used in chat completion.
  - `**kwargs`: Arbitrary keyword arguments for the chat completion service.

#### chat

```python
@staticmethod
async def chat(
	branch: 'Branch', instruction: 'Instruction' | str,
	context: Any | None = None, sender: str | None = None,
	system: 'System' | str | dict[str, Any] | None = None,
    actions: bool | 'T' | list[ T | str ] = False,
    out: bool = True, invoke: bool = True,
    **kwargs) -> Any:
    """Conducts a chat conversation with LLM, processing instructions and system messages, optionally invoking actions."""
```

- **Args**:
  - `branch`: The Branch instance to perform chat operations.
  - `instruction`: The instruction for the chat.
  - `context`: Additional context for the chat (optional).
  - `sender`: The sender of the chat message (optional).
  - `system`: System message to be processed (optional).
  - `actions`: Specifies actions to be invoked (using BaseActionNode).
  - `out`: If True, outputs the chat response.
  - `invoke`: If True, invokes actions as part of the chat.

#### ReAct

```python
@staticmethod
async def ReAct(
	branch: 'Branch', instruction: 'Instruction' | str,
    context: Any | None = None, sender: str | None = None,
    system: 'System' | str | dict[str, Any] | None = None,
    actions: bool | 'T' | list['T'] | str | list[str] | None = False,
    num_rounds: int = 1, **kwargs) -> None:
    """Performs a reason-action cycle with optional actions invocation over multiple rounds."""
```

- **Args**:
  - `branch`: The Branch instance to perform ReAct operations.
  - `instruction`: Initial instruction for the cycle.
  - `context`: Context relevant to the instruction (optional).
  - `sender`: Identifier for the message sender (optional).
  - `system`: Initial system message or configuration (optional).
  - `actions`: Tools to be registered or used during the cycle (using BaseActionNode).
  - `num_rounds`: Number of reason-action cycles to perform.

#### auto_followup

```python
@staticmethod
async def auto_followup(
	branch: 'Branch', instruction: 'Instruction' | str,
    context: Any | None = None, sender: str | None = None,
    system: 'System' | str | dict[str, Any] | None = None,
    actions: bool | 'T' | list['T'] | str | list[str] | None = False,
    max_followup: int = 3, out: bool = True, **kwargs) -> None:
    """Automatically performs follow-up actions based on chat interactions and actions invocations."""
```

- **Args**:
  - `branch`: The Branch instance to perform follow-up operations.
  - `instruction`: The initial instruction for follow-up.
  - `context`: Context relevant to the instruction (optional).
  - `sender`: Identifier for the message sender (optional).
  - `system`: Initial system message or configuration (optional).
  - `actions`: Specifies actions to be considered for follow-up actions (using BaseActionNode).
  - `max_followup`: Maximum number of follow-up chats allowed.
  - `out`: If True, outputs the result of the follow-up action.
