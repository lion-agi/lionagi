
### Methods:

#### Method: `chat`

**Signature**:
```python
async def chat(
    instruction: str = None,
    context: Any = None,
    system: Any = None,
    sender: str = None,
    recipient: str = None,
    branch: Branch = None,
    form: Any = None,
    confidence_score: float = None,
    reason: bool = False,
    **kwargs
) -> Any:
```

**Parameters**:
- `instruction` (str, optional): The instruction for the chat.
- `context` (Any, optional): The context to perform the instruction on.
- `system` (Any, optional): The system context for the chat.
- `sender` (str, optional): The sender of the instruction.
- `recipient` (str, optional): The recipient of the instruction.
- `branch` (Branch, optional): The branch to use for the chat.
- `form` (Any, optional): The form to create instruction from.
- `confidence_score` (float, optional): The confidence score for the operation.
- `reason` (bool, optional): Whether to include a reason for the operation.
- `**kwargs`: Additional keyword arguments for the chat operation.

**Returns**:
- `Any`: The result of the chat operation.

#### Method: `select`

**Signature**:
```python
async def select(
    instruction: str = None,
    context: Any = None,
    system: Any = None,
    sender: str = None,
    recipient: str = None,
    choices: list = None,
    branch: Branch = None,
    form: Any = None,
    confidence_score: float = None,
    reason: bool = False,
    **kwargs
) -> Any:
```

**Parameters**:
- `instruction` (str, optional): The instruction for the selection.
- `context` (Any, optional): The context to perform the instruction on.
- `system` (Any, optional): The system context for the selection.
- `sender` (str, optional): The sender of the instruction.
- `recipient` (str, optional): The recipient of the instruction.
- `choices` (list, optional): The choices for the selection.
- `branch` (Branch, optional): The branch to use for the selection.
- `form` (Any, optional): The form to create instruction from.
- `confidence_score` (float, optional): The confidence score for the operation.
- `reason` (bool, optional): Whether to include a reason for the operation.
- `**kwargs`: Additional keyword arguments for the selection operation.

**Returns**:
- `Any`: The result of the selection operation.

#### Method: `predict`

**Signature**:
```python
async def predict(
    instruction: str = None,
    context: Any = None,
    system: Any = None,
    sender: str = None,
    recipient: str = None,
    branch: Branch = None,
    form: Any = None,
    confidence_score: float = None,
    reason: bool = False,
    num_sentences: int = 1,
    **kwargs
) -> Any:
```

**Parameters**:
- `instruction` (str, optional): The instruction for the prediction.
- `context` (Any, optional): The context to perform the instruction on.
- `system` (Any, optional): The system context for the prediction.
- `sender` (str, optional): The sender of the instruction.
- `recipient` (str, optional): The recipient of the instruction.
- `branch` (Branch, optional): The branch to use for the prediction.
- `form` (Any, optional): The form to create instruction from.
- `confidence_score` (float, optional): The confidence score for the operation.
- `reason` (bool, optional): Whether to include a reason for the operation.
- `num_sentences` (int, optional): The number of sentences to generate in the prediction.
- `**kwargs`: Additional keyword arguments for the prediction operation.

**Returns**:
- `Any`: The result of the prediction operation.

#### Method: `act`

**Signature**:
```python
async def act(
    instruction: str = None,
    context: Any = None,
    system: Any = None,
    sender: str = None,
    recipient: str = None,
    branch: Branch = None,
    form: Any = None,
    confidence_score: float = None,
    reason: bool = False,
    **kwargs
) -> Any:
```

**Parameters**:
- `instruction` (str, optional): The instruction for the action.
- `context` (Any, optional): The context to perform the instruction on.
- `system` (Any, optional): The system context for the action.
- `sender` (str, optional): The sender of the instruction.
- `recipient` (str, optional): The recipient of the instruction.
- `branch` (Branch, optional): The branch to use for the action.
- `form` (Any, optional): The form to create instruction from.
- `confidence_score` (float, optional): The confidence score for the operation.
- `reason` (bool, optional): Whether to include a reason for the operation.
- `**kwargs`: Additional keyword arguments for the act operation.

**Returns**:
- `Any`: The result of the act operation.

#### Method: `score`

**Signature**:
```python
async def score(
    instruction: str = None,
    context: Any = None,
    system: Any = None,
    sender: str = None,
    recipient: str = None,
    branch: Branch = None,
    form: Any = None,
    confidence_score: float = None,
    reason: bool = False,
    score_range: tuple = None,
    include_endpoints: bool = None,
    num_digit: int = None,
    **kwargs
) -> Any:
```

**Parameters**:
- `instruction` (str, optional): Additional instruction for the scoring task.
- `context` (Any, optional): Context to perform the scoring task on.
- `system` (str, optional): System message to use for the scoring task.
- `sender` (str, optional): Sender of the instruction. Defaults to None.
- `recipient` (str, optional): Recipient of the instruction. Defaults to None.
- `branch` (Branch, optional): Branch to perform the task within. Defaults to a new Branch.
- `form` (Form, optional): Form to create the instruction from. Defaults to None.
- `confidence_score` (bool, optional): Flag to include a confidence score. Defaults to None.
- `reason` (bool, optional): Flag to include a reason for the scoring. Defaults to False.
- `score_range` (tuple, optional): Range for the score. Defaults to None.
- `include_endpoints` (bool, optional): Flag to include endpoints in the score range. Defaults to None.
- `num_digit` (int, optional): Number of decimal places for the score. Defaults to None.
- `**kwargs`: Additional keyword arguments for further customization.

**Returns**:
- `Any`: The result of the scoring task.

#### Method: `plan`

**Signature**:
```python
async def plan(
    instruction: str = None,
    context: Any = None,
    system: Any = None,
    sender: str = None,
    recipient: str = None,
    branch: Branch = None,
    form: Any = None,
    confidence_score: float = None,
    reason: bool = False,
    num_step: int = 3,
    **kwargs
) -> Any:
```

**Parameters**:
- `instruction` (str, optional): Additional instruction for the planning task.
- `context` (Any, optional): Context to perform the planning task on.
- `system` (str, optional): System message to use for the planning task.
- `sender` (str, optional): Sender of the instruction. Defaults to None.
- `recipient` (str, optional): Recipient of the instruction. Defaults to None.
- `branch` (Branch, optional): Branch to perform the task within. Defaults to a new Branch.
- `form` (Form, optional): Form to create the instruction from. Defaults to None.
- `confidence_score` (bool, optional): Flag to include a confidence score. Defaults to None.
- `reason` (bool, optional): Flag to include a reason for the plan. Defaults to False.
- `num_step` (int, optional): Number of steps in the plan. Defaults to 3.
- `**kwargs`: Additional keyword arguments for further customization.

**Returns**:
- `Any`: The result of the planning task.
