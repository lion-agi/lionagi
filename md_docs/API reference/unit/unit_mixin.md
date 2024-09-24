
### Class: `DirectiveMixin`

**Description**:
`DirectiveMixin` is a mixin class for handling chat operations and processing responses within a directive framework. It provides methods for creating chat configurations, calling and processing chat completions, and handling action requests.

### Methods:

#### `_create_chat_config`

**Signature**:
```python
def _create_chat_config(
    self,
    system: Optional[str] = None,
    instruction: Optional[str] = None,
    context: Optional[str] = None,
    images: Optional[str] = None,
    sender: Optional[str] = None,
    recipient: Optional[str] = None,
    request_fields: Optional[list] = None,
    form: Form = None,
    tools: bool = False,
    branch: Optional[Any] = None,
    **kwargs,
) -> Any
```

**Parameters**:
- `system` (Optional[str]): System message.
- `instruction` (Optional[str]): Instruction message.
- `context` (Optional[str]): Context message.
- `images` (Optional[str]): Images data.
- `sender` (Optional[str]): Sender identifier.
- `recipient` (Optional[str]): Recipient identifier.
- `request_fields` (Optional[list]): Fields requested in the response.
- `form` (Form): Form data.
- `tools` (bool): Flag indicating if tools should be used.
- `branch` (Optional[Any]): Branch instance.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `dict`: The chat configuration.

**Description**:
Creates the chat configuration based on the provided parameters.

#### `_call_chatcompletion`

**Signature**:
```python
async def _call_chatcompletion(
    self, imodel: Optional[Any] = None, branch: Optional[Any] = None, **kwargs
) -> Any
```

**Parameters**:
- `imodel` (Optional[Any]): The model instance.
- `branch` (Optional[Any]): The branch instance.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The chat completion result.

**Description**:
Calls the chat completion model.

#### `_process_chatcompletion`

**Signature**:
```python
async def _process_chatcompletion(
    self,
    payload: dict,
    completion: dict,
    sender: str,
    invoke_tool: bool = True,
    branch: Optional[Any] = None,
    action_request: Optional[Any] = None,
) -> Any
```

**Parameters**:
- `payload` (dict): The payload data.
- `completion` (dict): The completion data.
- `sender` (str): The sender identifier.
- `invoke_tool` (bool): Flag indicating if tools should be invoked.
- `branch` (Optional[Any]): The branch instance.
- `action_request` (Optional[Any]): The action request instance.

**Returns**:
- `Any`: The processed result.

**Description**:
Processes the chat completion response.

#### `_process_action_request`

**Signature**:
```python
async def _process_action_request(
    self,
    _msg: Optional[dict] = None,
    branch: Optional[Any] = None,
    invoke_tool: bool = True,
    action_request: Optional[Any] = None,
) -> Any
```

**Parameters**:
- `_msg` (Optional[dict]): The message data.
- `branch` (Optional[Any]): The branch instance.
- `invoke_tool` (bool): Flag indicating if tools should be invoked.
- `action_request` (Optional[Any]): The action request instance.

**Returns**:
- `Any`: The processed result.

**Description**:
Processes an action request from the assistant response.

#### `_output`

**Signature**:
```python
async def _output(
    self,
    payload: dict,
    completion: dict,
    sender: str,
    invoke_tool: bool,
    request_fields: dict,
    form: Form = None,
    return_form: bool = True,
    strict: bool = False,
    rulebook: Any = None,
    use_annotation: bool = True,
    template_name: str = None,
) -> Any
```

**Parameters**:
- `payload` (dict): The payload data.
- `completion` (dict): The completion data.
- `sender` (str): The sender identifier.
- `invoke_tool` (bool): Flag indicating if tools should be invoked.
- `request_fields` (dict): Fields requested in the response.
- `form` (Form): Form data.
- `return_form` (bool): Flag indicating if form should be returned.
- `strict` (bool): Flag indicating if strict validation should be applied.
- `rulebook` (Any): Rulebook instance for validation.
- `use_annotation` (bool): Flag indicating if annotations should be used.
- `template_name` (str): Template name for form.

**Returns**:
- `Any`: The processed response.

**Description**:
Outputs the final processed response.

#### `_base_chat`

**Signature**:
```python
async def _base_chat(
    self,
    instruction: Any = None,
    *,
    system: Any = None,
    context: Any = None,
    sender: Any = None,
    recipient: Any = None,
    request_fields: dict = None,
    form: Form = None,
    tools: Any = False,
    images: Optional[str] = None,
    invoke_tool: bool = True,
    return_form: bool = True,
    strict: bool = False,
    rulebook: Any = None,
    imodel: Any = None,
    use_annotation: bool = True,
    branch: Any = None,
    clear_messages: bool = False,
    return_branch: bool = False,
    **kwargs,
) -> Any
```

**Parameters**:
- `instruction` (Any, optional): Instruction message.
- `system` (Any, optional): System message.
- `context` (Any, optional): Context message.
- `sender` (Any, optional): Sender identifier.
- `recipient` (Any, optional): Recipient identifier.
- `request_fields` (dict, optional): Fields requested in the response.
- `form` (Form, optional): Form data.
- `tools` (Any, optional): Flag indicating if tools should be used.
- `images` (Optional[str], optional): Images data.
- `invoke_tool` (bool, optional): Flag indicating if tools should be invoked.
- `return_form` (bool, optional): Flag indicating if form should be returned.
- `strict` (bool, optional): Flag indicating if strict validation should be applied.
- `rulebook` (Any, optional): Rulebook instance for validation.
- `imodel` (Any, optional): Model instance.
- `use_annotation` (bool, optional): Flag indicating if annotations should be used.
- `branch` (Any, optional): Branch instance.
- `clear_messages` (bool, optional): Flag indicating if messages should be cleared.
- `return_branch` (bool, optional): Flag indicating if branch should be returned.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The processed response and branch.

**Description**:
Handles the base chat operation by configuring the chat and processing the response.

#### `_chat`

**Signature**:
```python
async def _chat(
    self,
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    request_fields=None,
    form: Form = None,
    tools=False,
    invoke_tool=True,
    return_form=True,
    strict=False,
    rulebook=None,
    imodel=None,
    images: Optional[str] = None,
    clear_messages=False,
    use_annotation=True,
    timeout: float = None,
    return_branch=False,
    **kwargs,
) -> Any
```

**Parameters**:
- `instruction` (Any, optional): Instruction message.
- `context` (Any, optional): Context message.
- `system` (Any, optional): System message.
- `sender` (Any, optional): Sender identifier.
- `recipient` (Any, optional): Recipient identifier.
- `branch` (Any, optional): Branch instance.
- `request_fields` (dict, optional): Fields requested in the response.
- `form` (Form, optional): Form data.
- `tools` (Any, optional): Flag indicating if tools should be used.
- `invoke_tool` (bool, optional): Flag indicating if tools should be invoked.
- `return_form` (bool, optional): Flag indicating if form should be returned.
- `strict` (bool, optional): Flag indicating if strict validation should be applied.
- `rulebook` (Any, optional): Rulebook instance for validation.
- `imodel` (Any, optional): Model instance.
- `clear_messages` (bool, optional): Flag indicating if messages should be cleared.
- `use_annotation` (bool, optional): Flag indicating if annotations should be used.
- `timeout` (float, optional): Timeout value.
- `return_branch` (bool, optional): Flag indicating if branch should be returned.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The processed response.

**Description**:
Handles the chat operation.

#### `_direct`

**Signature**:
```python
async def _direct(
    self,
    instruction=None,
    context=None,
    form: Form = None,
    branch=None,
    tools=None,
    reason: bool = None,
    predict: bool = None,
    score: bool = None,
    select: bool = None,
    plan: bool = None,
    allow_action: bool = None,
    allow_extension: bool = None,
    confidence: bool = None,
    max_extension: int = None,
    score_num

_digits=None,
    score_range=None,
    select_choices=None,
    plan_num_step=None,
    predict_num_sentences=None,
    clear_messages=False,
    return_branch=False,
    images: Optional[str] = None,
    **kwargs,
) -> Any
```

**Parameters**:
- `instruction` (Any, optional): Instruction message.
- `context` (Any, optional): Context message.
- `form` (Form, optional): Form data.
- `branch` (Any, optional): Branch instance.
- `tools` (Any, optional): Tools data.
- `reason` (bool, optional): Flag indicating if reason should be included.
- `predict` (bool, optional): Flag indicating if prediction should be included.
- `score` (bool, optional): Flag indicating if score should be included.
- `select` (bool, optional): Flag indicating if selection should be included.
- `plan` (bool, optional): Flag indicating if plan should be included.
- `allow_action` (bool, optional): Flag indicating if action should be allowed.
- `allow_extension` (bool, optional): Flag indicating if extension should be allowed.
- `confidence` (bool, optional): Flag indicating if confidence should be included.
- `max_extension` (int, optional): Maximum extension value.
- `score_num_digits` (int, optional): Number of digits for score.
- `score_range` (tuple, optional): Range for score.
- `select_choices` (list, optional): Choices for selection.
- `plan_num_step` (int, optional): Number of steps for plan.
- `predict_num_sentences` (int, optional): Number of sentences for prediction.
- `clear_messages` (bool, optional): Flag indicating if messages should be cleared.
- `return_branch` (bool, optional): Flag indicating if branch should be returned.
- `images` (Optional[str], optional): Images data.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The processed response and branch.

**Description**:
Directs the operation based on the provided parameters.

#### `_base_direct`

**Signature**:
```python
async def _base_direct(
    self,
    instruction=None,
    *,
    context=None,
    form: Form = None,
    branch=None,
    tools=None,
    reason: bool = None,
    predict: bool = None,
    score: bool = None,
    select: bool = None,
    plan: bool = None,
    allow_action: bool = None,
    allow_extension: bool = None,
    confidence: bool = None,
    max_extension: int = None,
    score_num_digits=None,
    score_range=None,
    select_choices=None,
    plan_num_step=None,
    predict_num_sentences=None,
    clear_messages=False,
    return_branch=False,
    images: Optional[str] = None,
    **kwargs,
) -> Any
```

**Parameters**:
- `instruction` (Any, optional): Instruction message.
- `context` (Any, optional): Context message.
- `form` (Form, optional): Form data.
- `branch` (Any, optional): Branch instance.
- `tools` (Any, optional): Tools data.
- `reason` (bool, optional): Flag indicating if reason should be included.
- `predict` (bool, optional): Flag indicating if prediction should be included.
- `score` (bool, optional): Flag indicating if score should be included.
- `select` (bool, optional): Flag indicating if selection should be included.
- `plan` (bool, optional): Flag indicating if plan should be included.
- `allow_action` (bool, optional): Flag indicating if action should be allowed.
- `allow_extension` (bool, optional): Flag indicating if extension should be allowed.
- `confidence` (bool, optional): Flag indicating if confidence should be included.
- `max_extension` (int, optional): Maximum extension value.
- `score_num_digits` (int, optional): Number of digits for score.
- `score_range` (tuple, optional): Range for score.
- `select_choices` (list, optional): Choices for selection.
- `plan_num_step` (int, optional): Number of steps for plan.
- `predict_num_sentences` (int, optional): Number of sentences for prediction.
- `clear_messages` (bool, optional): Flag indicating if messages should be cleared.
- `return_branch` (bool, optional): Flag indicating if branch should be returned.
- `images` (Optional[str], optional): Images data.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The processed response and branch.

**Description**:
Handles the base direct operation.

#### `_extend`

**Signature**:
```python
async def _extend(
    self,
    tools,
    reason,
    predict,
    score,
    select,
    plan,
    allow_action,
    confidence,
    score_num_digits,
    score_range,
    select_choices,
    predict_num_sentences,
    allow_extension,
    max_extension,
    **kwargs,
) -> Any
```

**Parameters**:
- `tools` (Any): Tools data.
- `reason` (bool): Flag indicating if reason should be included.
- `predict` (bool): Flag indicating if prediction should be included.
- `score` (bool): Flag indicating if score should be included.
- `select` (bool): Flag indicating if selection should be included.
- `plan` (Any): Plan data.
- `allow_action` (bool): Flag indicating if action should be allowed.
- `confidence` (bool): Flag indicating if confidence should be included.
- `score_num_digits` (int): Number of digits for score.
- `score_range` (tuple): Range for score.
- `select_choices` (list): Choices for selection.
- `predict_num_sentences` (int): Number of sentences for prediction.
- `allow_extension` (bool): Flag indicating if extension should be allowed.
- `max_extension` (int): Maximum extension value.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `list`: The extended forms.

**Description**:
Handles the extension of the form based on the provided parameters.

#### `_act`

**Signature**:
```python
async def _act(self, form, branch, actions=None) -> Any
```

**Parameters**:
- `form` (Any): Form data.
- `branch` (Any): Branch instance.
- `actions` (Any): Actions data.

**Returns**:
- `dict`: The updated form.

**Description**:
Processes actions based on the provided form and actions.

#### `_select`

**Signature**:
```python
async def _select(
    self,
    form=None,
    choices=None,
    reason=False,
    confidence_score=None,
    instruction=None,
    template=None,
    context=None,
    branch=None,
    **kwargs,
) -> Any
```

**Parameters**:
- `form` (Any, optional): Form data.
- `choices` (Any, optional): Choices for the selection.
- `reason` (bool, optional): Flag indicating if reason should be included.
- `confidence_score` (Any, optional): Confidence score for the selection.
- `instruction` (Any, optional): Instruction for the selection.
- `template` (Any, optional): Template for the selection.
- `context` (Any, optional): Context data.
- `branch` (Any, optional): Branch instance.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The selection response.

**Description**:
Selects a response based on the provided parameters.

#### `_predict`

**Signature**:
```python
async def _predict(
    self,
    form=None,
    num_sentences=None,
    reason=False,
    confidence_score=None,
    instruction=None,
    context=None,
    branch=None,
    template=None,
    **kwargs,
) -> Any
```

**Parameters**:
- `form` (Any, optional): Form data.
- `num_sentences` (int, optional): Number of sentences for the prediction.
- `reason` (bool, optional): Flag indicating if reason should be included.
- `confidence_score` (Any, optional): Confidence score for the prediction.
- `instruction` (Any, optional): Instruction for the prediction.
- `context` (Any, optional): Context data.
- `branch` (Any, optional): Branch instance.
- `template` (Any, optional): Template for the prediction.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The prediction response.

**Description**:
Predicts a response based on the provided parameters.

#### `_score`

**Signature**:
```python
async def _score(
    self,
    form=None,
    score_range=None,
    include_endpoints=None,
    num_digit=None,
    reason=False,
    confidence_score=None,
    instruction=None,
    context=None,
    branch=None,
    template=None,
    **kwargs,
) -> Any
```

**Parameters**:
- `form` (Any, optional): Form data.
- `score_range` (tuple, optional): Range for score.
- `include_endpoints` (bool, optional): Flag indicating if endpoints should be included.
- `num_digit` (int, optional): Number of digits for score.
- `reason` (bool, optional): Flag indicating if reason should be included.
- `confidence_score` (Any, optional): Confidence score for the score.
- `instruction` (Any, optional): Instruction for the score.
- `context` (Any, optional): Context data.
- `branch` (Any, optional): Branch instance.
- `template` (Any, optional): Template for the score.
- `kwargs`: Additional keyword arguments.

**

Returns**:
- `Any`: The score response.

**Description**:
Scores a response based on the provided parameters.

#### `_plan`

**Signature**:
```python
async def _plan(
    self,
    form=None,
    num_step=None,
    reason=False,
    confidence_score=None,
    instruction=None,
    context=None,
    branch=None,
    template=None,
    **kwargs,
) -> Any
```

**Parameters**:
- `form` (Any, optional): Form data.
- `num_step` (int, optional): Number of steps for the plan.
- `reason` (bool, optional): Flag indicating if reason should be included.
- `confidence_score` (Any, optional): Confidence score for the plan.
- `instruction` (Any, optional): Instruction for the plan.
- `context` (Any, optional): Context data.
- `branch` (Any, optional): Branch instance.
- `template` (Any, optional): Template for the plan.
- `kwargs`: Additional keyword arguments.

**Returns**:
- `Any`: The plan response.

**Description**:
Plans a response based on the provided parameters.

#### `_process_model_response`

**Signature**:
```python
def _process_model_response(content_, request_fields) -> Any
```

**Parameters**:
- `content_` (Any): The content data.
- `request_fields` (list): Fields requested in the response.

**Returns**:
- `Any`: The processed response.

**Description**:
Processes the model response content.
