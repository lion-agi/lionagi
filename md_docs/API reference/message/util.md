
### Function: `create_message`

**Description**:
Creates a message based on the provided parameters. This function handles the creation of various types of messages such as system messages, instructions, assistant responses, action requests, and action responses.

**Signature**:
```python
def create_message(
    *,
    system=None,
    instruction=None,
    context=None,
    assistant_response=None,
    function=None,
    arguments=None,
    func_outputs=None,
    action_request=None,
    action_response=None,
    images=None,
    sender=None,
    recipient=None,
    requested_fields=None,
    **kwargs,
) -> RoledMessage:
```

**Parameters**:
- `system` (dict, optional): The system node (JSON serializable).
- `instruction` (dict, optional): The instruction node (JSON serializable).
- `context` (dict, optional): Additional context (JSON serializable).
- `assistant_response` (dict, optional): The assistant response node (JSON serializable).
- `function` (str, optional): The function name for action requests.
- `arguments` (dict, optional): The arguments for the function.
- `func_outputs` (Any, optional): The outputs from the function.
- `action_request` (ActionRequest, optional): The action request node.
- `action_response` (ActionResponse, optional): The action response node.
- `images` (list, optional): The image content in base64 encoding.
- `sender` (str, optional): The sender of the message.
- `recipient` (str, optional): The recipient of the message.
- `requested_fields` (dict[str, str], optional): The requested fields for the instruction.
- `**kwargs`: Additional context fields.

**Return Values**:
- `RoledMessage`: The constructed message based on the provided parameters.

**Exceptions Raised**:
- `ValueError`: If the parameters are invalid or missing required values.

**Usage Examples**:
```python
# Creating a system message
system_message = create_message(system={"status": "active"}, sender="system", recipient="user")

# Creating an instruction message
instruction_message = create_message(
    instruction="Please provide the status.",
    context={"user_id": 12345},
    sender="user",
    recipient="assistant",
    requested_fields={"status": "The current status of the system."}
)

# Creating an action request
action_request = create_message(
    function="get_status",
    arguments={"user_id": 12345},
    sender="user",
    recipient="system"
)

# Creating an action response
action_response = create_message(
    action_request=action_request,
    func_outputs={"status": "active"},
    sender="system"
)
```

### Function: `_parse_action_request`

**Description**:
Parses an action request from the response.

**Signature**:
```python
def _parse_action_request(response: dict) -> list[ActionRequest] | None:
```

**Parameters**:
- `response` (dict): The response containing the action request.

**Return Values**:
- `list[ActionRequest]` or `None`: A list of action requests or None if invalid.

**Exceptions Raised**:
- `ActionError`: If the action request is invalid.

**Usage Examples**:
```python
response = {
    "content": {
        "tool_uses": [
            {"action": "action_get_status", "arguments": {"user_id": 12345}}
        ]
    }
}
action_requests = _parse_action_request(response)
```

### Function: `_handle_action_request`

**Description**:
Handles the action request parsing from the response.

**Signature**:
```python
def _handle_action_request(response: dict) -> list[dict]:
```

**Parameters**:
- `response` (dict): The response containing the action request details.

**Return Values**:
- `list[dict]`: A list of function call details.

**Exceptions Raised**:
- `ValueError`: If the response message is invalid.

**Usage Examples**:
```python
response = {
    "tool_calls": [
        {
            "type": "function",
            "function": {
                "name": "get_status",
                "arguments": {"user_id": 12345}
            }
        }
    ]
}
function_calls = _handle_action_request(response)
```
