
### Class: `Unit`

**Description**:
`Unit` is a class that extends `Directive` and `DirectiveMixin` to provide advanced operations like chat, direct actions, and predictions using a specific branch and model. It integrates various functionalities, including handling form templates, validation, and retry logic.

### Methods:

#### `__init__`

**Signature**:
```python
def __init__(self, branch, imodel: iModel = None, template=None, rulebook=None) -> None:
```

**Parameters**:
- `branch` (Branch): The branch instance associated with the `Unit`.
- `imodel` (iModel, optional): The model instance to use. Defaults to the branch's model.
- `template` (Type[Form], optional): The form template to use for operations. Defaults to `UnitForm`.
- `rulebook` (Rulebook, optional): The rulebook for response validation.

**Description**:
Initializes the `Unit` instance with the specified branch, model, form template, and rulebook.

#### `chat`

**Signature**:
```python
async def chat(
    self,
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    request_fields=None,
    form=None,
    tools=False,
    invoke_tool=True,
    return_form=True,
    strict=False,
    rulebook=None,
    imodel=None,
    clear_messages=False,
    use_annotation=True,
    return_branch=False,
    **kwargs,
):
```

**Parameters**:
- `instruction` (str, optional): Instruction message.
- `context` (str, optional): Context message.
- `system` (str, optional): System message.
- `sender` (str, optional): Sender identifier.
- `recipient` (str, optional): Recipient identifier.
- `branch` (Branch, optional): Branch instance.
- `request_fields` (list, optional): Fields requested in the response.
- `form` (Form, optional): Form data.
- `tools` (bool, optional): Flag indicating if tools should be used.
- `invoke_tool` (bool, optional): Flag indicating if tools should be invoked.
- `return_form` (bool, optional): Flag indicating if form should be returned.
- `strict` (bool, optional): Flag indicating if strict validation should be applied.
- `rulebook` (Rulebook, optional): Rulebook instance for validation.
- `imodel` (iModel, optional): Model instance.
- `clear_messages` (bool, optional): Flag indicating if messages should be cleared.
- `use_annotation` (bool, optional): Flag indicating if annotations should be used.
- `return_branch` (bool, optional): Flag indicating if branch should be returned.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The processed response.

**Description**:
Asynchronously performs a chat operation.

#### `direct`

**Signature**:
```python
async def direct(
    self,
    instruction=None,
    *,
    context=None,
    form=None,
    branch=None,
    tools=None,
    return_branch=False,
    reason: bool = False,
    predict: bool = False,
    score=None,
    select=None,
    plan=None,
    allow_action: bool = False,
    allow_extension: bool = False,
    max_extension: int = None,
    confidence=None,
    score_num_digits=None,
    score_range=None,
    select_choices=None,
    plan_num_step=None,
    predict_num_sentences=None,
    directive: str = None,
    **kwargs,
)
```

**Parameters**:
- `instruction` (str, optional): Instruction message.
- `context` (str, optional): Context message.
- `form` (Form, optional): Form data.
- `branch` (Branch, optional): Branch instance.
- `tools` (Any, optional): Tools to be used.
- `return_branch` (bool, optional): Flag indicating if branch should be returned.
- `reason` (bool, optional): Flag indicating if reason should be included.
- `predict` (bool, optional): Flag indicating if prediction should be included.
- `score` (Any, optional): Score parameters.
- `select` (Any, optional): Select parameters.
- `plan` (Any, optional): Plan parameters.
- `allow_action` (bool, optional): Flag indicating if action should be allowed.
- `allow_extension` (bool, optional): Flag indicating if extension should be allowed.
- `max_extension` (int, optional): Maximum extension value.
- `confidence` (Any, optional): Confidence parameters.
- `score_num_digits` (int, optional): Number of digits for score.
- `score_range` (tuple, optional): Range for score.
- `select_choices` (list, optional): Choices for selection.
- `plan_num_step` (int, optional): Number of steps for plan.
- `predict_num_sentences` (int, optional): Number of sentences for prediction.
- `directive` (str, optional): Directive for the operation.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The processed response.

**Description**:
Asynchronously directs the operation based on the provided parameters.

#### `select`

**Signature**:
```python
async def select(self, *args, **kwargs):
```

**Parameters**:
- `args`: Positional arguments to pass to the `_select` method.
- `kwargs`: Keyword arguments to pass to the `_select` method, including retry configurations.

**Returns**:
- `Any`: The result of the select operation.

**Description**:
Asynchronously performs a select operation using the `_select` method with retry logic.

#### `predict`

**Signature**:
```python
async def predict(self, *args, **kwargs):
```

**Parameters**:
- `args`: Positional arguments to pass to the `_predict` method.
- `kwargs`: Keyword arguments to pass to the `_predict` method, including retry configurations.

**Returns**:
- `Any`: The result of the predict operation.

**Description**:
Asynchronously performs a predict operation using the `_predict` method with retry logic.

#### `score`

**Signature**:
```python
async def score(self, *args, **kwargs):
```

**Parameters**:
- `args`: Positional arguments to pass to the `_score` method.
- `kwargs`: Keyword arguments to pass to the `_score` method, including retry configurations.

**Returns**:
- `Any`: The result of the score operation.

**Description**:
Asynchronously performs a score operation using the `_score` method with retry logic.

#### `plan`

**Signature**:
```python
async def plan(self, *args, **kwargs):
```

**Parameters**:
- `args`: Positional arguments to pass to the `_plan` method.
- `kwargs`: Keyword arguments to pass to the `_plan` method, including retry configurations.

**Returns**:
- `Any`: The result of the plan operation.

**Description**:
Asynchronously performs a plan operation using the `_plan` method with retry logic.

#### `_mono_direct`

**Signature**:
```python
async def _mono_direct(
    self,
    directive: str,
    instruction=None,
    context=None,
    system=None,
    branch=None,
    tools=None,
    template=None,
    **kwargs,
)
```

**Parameters**:
- `directive` (str): The directive for the operation.
- `instruction` (str, optional): Additional instruction.
- `context` (str, optional): Context for the operation.
- `system` (str, optional): System message.
- `branch` (Branch, optional): Branch instance.
- `tools` (Any, optional): Tools to be used.
- `template` (Any, optional): Template for the operation.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The result of the direct operation.

**Description**:
Asynchronously performs a single direct operation.
