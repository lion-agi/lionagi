## PolyChat Class
The `PolyChat` class is designed to facilitate parallel chat conversations with multiple branches in a controlled and efficient manner, extending the `BasePolyFlow` class.

### Attributes
- None explicitly defined beyond initialization parameters.

### Methods

#### __init__
Initializes a `PolyChat` instance with a session context.
- **Parameters**:
  - `session`: The session context which manages state across multiple branches.
- **Returns**:
  - None

#### parallel_chat
Initiates parallel chat conversations across multiple branch instances with specified configurations.
- **Parameters**:
  - `instruction (Instruction | str)`: The instruction for the chat.
  - `num_instances (int)`: Number of parallel instances to execute.
  - `context (Optional[Any])`: Additional context for the chat.
  - `sender (Optional[str])`: Identifier for the sender.
  - `branch_system (Optional[Any])`: System configurations for branches.
  - `messages (Optional[Any])`: Initial messages for the branches.
  - `tools (bool)`: Specifies if tools should be used.
  - `out (bool)`: Whether to output the chat results.
  - `invoke (bool)`: Whether to invoke tools during the chat.
  - `output_fields (Optional[Any])`: Specifies the fields to output.
  - `persist_path (Optional[str])`: Path for persisting branch data.
  - `branch_config (Optional[dict])`: Additional configurations for branches.
  - `explode (bool)`: If True, expands combinations of instructions and contexts.
  - `**kwargs`: Additional arguments for chat configuration.
- **Returns**:
  - `Any`: Results from the parallel chat sessions.

#### _parallel_chat
A private method that performs the actual parallel chat operations internally within the class.
- **Parameters**:
  - Similar to `parallel_chat`, but includes `include_mapping` to decide if mapping info should be returned, and `default_key` for response formatting.
- **Returns**:
  - `Any`: The results from the parallel chat operations, potentially including mapping details if `include_mapping` is True.

### Usage Example
```python
# Assuming a session context is already configured
poly_chat = PolyChat(session)
results = await poly_chat.parallel_chat(
    instruction="How can we improve user experience?",
    num_instances=3,
    context={"previous_interaction": "user feedback"},
    tools=True,
    output_fields={"summary": True},
    persist_path="/data/branch_chats"
)
