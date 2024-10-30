# Instruction API Documentation

The `Instruction` class represents an instruction message in the LION system. It contains detailed information about the instruction, including context, guidance, and request fields.

## Class: Instruction

Inherits from: `RoledMessage`

### Attributes

- `content: Note` - The content of the instruction message.

### Methods

#### `__init__(instruction: Any | MessageFlag, context: Any | MessageFlag = None, guidance: Any | MessageFlag = None, images: list | MessageFlag = None, sender: Any | MessageFlag = None, recipient: Any | MessageFlag = None, request_fields: dict | MessageFlag = None, image_detail: Literal["low", "high", "auto"] | MessageFlag = None, protected_init_params: dict | None = None)`

Initializes an Instruction instance.

- **Parameters:**
  - `instruction: Any | MessageFlag` - The main instruction content.
  - `context: Any | MessageFlag` - The context for the instruction (optional).
  - `guidance: Any | MessageFlag` - Guidance for the instruction (optional).
  - `images: list | MessageFlag` - List of images related to the instruction (optional).
  - `sender: Any | MessageFlag` - The sender of the instruction (optional).
  - `recipient: Any | MessageFlag` - The recipient of the instruction (optional).
  - `request_fields: dict | MessageFlag` - Fields to be requested (optional).
  - `image_detail: Literal["low", "high", "auto"] | MessageFlag` - Detail level for images (optional).
  - `protected_init_params: dict | None` - Protected initialization parameters (optional).

#### `update_images(images: list | str, image_detail: Literal["low", "high", "auto"] = None)`

Add new images and update the image detail level.

- **Parameters:**
  - `images: list | str` - New images to add.
  - `image_detail: Literal["low", "high", "auto"]` - New image detail level (optional).

#### `update_guidance(guidance: str)`

Update the guidance content of the instruction.

- **Parameters:**
  - `guidance: str` - New guidance content.
- **Raises:**
  - `LionTypeError` - If guidance is not a string.

#### `update_request_fields(request_fields: dict)`

Update the requested fields in the instruction.

- **Parameters:**
  - `request_fields: dict` - New request fields to update.

#### `update_context(*args, **kwargs)`

Add new context to the instruction.

- **Parameters:**
  - `*args: Any` - Positional arguments to add to context.
  - `**kwargs: Any` - Keyword arguments to add to context.

### Class Methods

#### `from_form(form: BaseForm | Type[Form], sender: str | None = None, recipient: Any = None, images: str | None = None, image_detail: str | None = None, strict: bool = None, assignment: str = None, task_description: str = None, fill_inputs: bool = True, none_as_valid_value: bool = False, input_value_kwargs: dict = None) -> Instruction`

Create an Instruction instance from a form.

- **Parameters:** (see method signature for details)
- **Returns:**
  - `Instruction` - A new Instruction instance created from the form.
- **Raises:**
  - `LionTypeError` - If the provided form is invalid.

### Properties

- `guidance: Any` - Returns the guidance content.
- `instruction: Any` - Returns the main instruction content.

### Usage Example

```python
instruction = Instruction(
    instruction="Calculate the sum of two numbers",
    context={"operation": "addition"},
    guidance="Use the provided calculator function",
    sender="user_1",
    recipient="math_service",
    request_fields={"num1": "int", "num2": "int"}
)

print(instruction.instruction)  # Output: Calculate the sum of two numbers
instruction.update_guidance("Ensure both numbers are positive integers")
print(instruction.guidance)  # Output: Ensure both numbers are positive integers
```

This example demonstrates how to create an Instruction instance and use its methods to update content.
