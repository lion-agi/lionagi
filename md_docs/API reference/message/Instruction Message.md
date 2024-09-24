
### Class: `Instruction`

**Parent Class:** [[Roled Message#^f41a31|RoledMessage]]

**Description**:
`Instruction` represents an instruction message with additional context and requested fields. It inherits from `RoledMessage` and provides methods to manage context and requested fields specific to instructions.

#### Attributes:
- `instruction` (str): The instruction content.
- `context` (dict or str): Additional context for the instruction.
- `sender` (): The sender of the instruction.
- `recipient` (): The recipient of the instruction.
- `request_fields` (dict): Fields requested in the instruction.

### `__init__`

**Signature**:
```python
def __init__(
    instruction: str | None = None,
    context: dict | str | None = None,
    images: list | None = None,
    sender = None,
    recipient = None,
    request_fields: dict | None = None,
    additional_context: dict | None = None,
    image_detail: str | None = None,
    **kwargs,
)
```

**Parameters**:
- `instruction` (str, optional): The instruction content.
- `context` (dict or str, optional): Additional context for the instruction.
- `images` (list, optional): The image content in base64 encoding.
- `sender` (, optional): The sender of the instruction.
- `recipient` (, optional): The recipient of the instruction.
- `request_fields` (dict, optional): Fields requested in the instruction.
- `additional_context` (dict, optional): Additional context for the instruction.
- `image_detail` (str, optional): The detail level for images. Defaults to "low".
- `**kwargs`: Additional keyword arguments to be passed to the parent class.

**Description**:
Initializes the `Instruction` message.

**Usage Examples**:
```python
instruction = Instruction(
    instruction="Analyze data",
    context={"data": "sample_data"},
    sender="user_1",
    recipient="processor_1",
    request_fields={"result": "analysis_result"}
)
print(instruction.instruct)  # Output: Analyze data
```

### `instruct`

**Signature**:
```python
@property
def instruct() -> str:
```

**Return Values**:
- `str`: The instruction content.

**Description**:
Returns the instruction content.

**Usage Examples**:
```python
instruction = Instruction(instruction="Analyze data")
print(instruction.instruct)  # Output: Analyze data
```

### `clone`

**Signature**:
```python
def clone(self, **kwargs) -> Instruction:
```

**Parameters**:
- `**kwargs`: Optional keyword arguments to be included in the cloned object.

**Return Values**:
- `Instruction`: A new instance of the object with the same content and additional keyword arguments.

**Description**:
Creates a copy of the current `Instruction` object with optional additional arguments.

**Usage Examples**:
```python
new_instruction = instruction.clone(sender="new_sender")
print(new_instruction.sender)  # Output: new_sender
print(new_instruction.instruct)  # Output: Analyze data
```

### `_add_context`

**Signature**:
```python
def _add_context(self, context: dict | str | None = None, **kwargs):
```

**Parameters**:
- `context` (dict or str, optional): Additional context to be added.
- `**kwargs`: Additional context fields to be added.

**Description**:
Adds context to the instruction message.

**Usage Examples**:
```python
instruction = Instruction(instruction="Analyze data")
instruction._add_context(context={"additional_info": "important"})
print(instruction.content["context"])  # Output: {'additional_info': 'important'}
```

### `_update_request_fields`

**Signature**:
```python
def _update_request_fields(self, request_fields: dict):
```

**Parameters**:
- `request_fields` (dict): The fields requested in the instruction.

**Description**:
Updates the requested fields in the instruction message.

**Usage Examples**:
```python
instruction = Instruction(instruction="Analyze data")
instruction._update_request_fields({"result": "analysis_result"})
print(instruction.content["request_fields"])  # Output: {'result': 'analysis_result'}
```

### `from_form`

**Signature**:
```python
@classmethod
def from_form(
    cls,
    form: Form,
    sender: str | None = None,
    recipient=None,
    image=None,
) -> Instruction:
```

**Parameters**:
- `form` (Form): The form containing instruction details.
- `sender` (str, optional): The sender of the instruction.
- `recipient` (, optional): The recipient of the instruction.
- `image` (str, optional): The image content in base64 encoding.

**Return Values**:
- `Instruction`: The created `Instruction` instance.

**Description**:
Creates an `Instruction` instance from a form.

**Usage Examples**:
```python
form = Form(
    _instruction_prompt="Analyze data",
    _instruction_context={"data": "sample_data"},
    _instruction_request_fields={"result": "analysis_result"}
)
instruction = Instruction.from_form(form)
print(instruction.instruct)  # Output: Analyze data
```
