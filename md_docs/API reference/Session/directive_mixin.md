
### Class: `DirectiveMixin`

**Description**:
`DirectiveMixin` is a mixin class that provides functionalities for handling chat interactions within a directive framework. It includes methods for processing instructions, interacting with tools, models, and validation rules, managing retries, timeouts, and concurrency.

### Method: `chat`

**Signature**:
```python
async def chat(
    self,
    instruction,  # additional instruction
    context=None,  # context to perform the instruction on
    system=None,  # optionally swap system message
    sender=None,  # sender of the instruction, default "user"
    recipient=None,  # recipient of the instruction, default "branch.ln_id"
    requested_fields=None,  # fields to request from the context, default None
    form=None,  # form to create instruction from, default None,
    tools=False,  # the tools to use, use True to consider all tools, no tools by default
    invoke_tool=True,  # whether to invoke the tool when function calling, default True
    return_form=True,  # whether to return the form if a form is passed in, otherwise return a dict/str
    strict=False,  # whether to strictly enforce the rule validation, default False
    rulebook=None,  # the rulebook to use for validation, default None, use default rulebook
    imodel=None,  # the optionally swappable iModel for the commands, otherwise self.branch.imodel
    clear_messages=False,
    use_annotation=True,  # whether to use annotation as rule qualifier, default True, (need rulebook if False)
    retries: int = 3,
    delay: float = 0,
    backoff_factor: float = 1,
    default=None,
    timeout: float = None,
    timing: bool = False,
    return_branch=False,
    images=None,
    image_path=None,
    **kwargs,
) -> Any:
```

**Parameters**:
- `instruction` (str, optional): Additional instruction to process.
- `context` (Any, optional): Context to perform the instruction on.
- `system` (str, optional): Optionally swap the system message.
- `sender` (str, optional): Sender of the instruction, default is "user".
- `recipient` (str, optional): Recipient of the instruction, default is "branch.ln_id".
- `requested_fields` (dict[str, str], optional): Fields to request from the context.
- `form` (Any, optional): Form to create instruction from, default is None.
- `tools` (bool, optional): Tools to use, use True to consider all tools, no tools by default.
- `invoke_tool` (bool, optional): Whether to invoke the tool when function calling, default is True.
- `return_form` (bool, optional): Whether to return the form if a form is passed in, otherwise return a dict/str.
- `strict` (bool, optional): Whether to strictly enforce rule validation, default is False.
- `rulebook` (Any, optional): The rulebook to use for validation, default is None (uses default rulebook).
- `imodel` (iModel, optional): Optionally swappable iModel for the commands, otherwise self.branch.imodel.
- `clear_messages` (bool, optional): Whether to clear previous messages, default is False.
- `use_annotation` (bool, optional): Whether to use annotation as rule qualifier, default is True (needs rulebook if False).
- `retries` (int, optional): Number of retries if failed, default is 3.
- `delay` (float, optional): Number of seconds to delay before retrying, default is 0.
- `backoff_factor` (float, optional): Exponential backoff factor, default is 1 (no backoff).
- `default` (Any, optional): Default value to return if all retries failed.
- `timeout` (float, optional): Timeout for the rcall, default is None (no timeout).
- `timing` (bool, optional): If True, will return a tuple (output, duration), default is False.
- `return_branch` (bool, optional): Whether to return the branch after processing, default is False.
- `images` (Any, optional): Base64 encoded image content.
- `image_path` (str, optional): Path to image to be read and converted to base64.
- `kwargs`: Additional keyword arguments for further customization.

**Return Values**:
- `Any`: The result of the chat processing, format determined by the `return_form` parameter.

**Description**:
Asynchronously handles a chat interaction within the directive framework. This method processes an instruction with the given context and optional parameters, interacting with tools, models, and validation rules as needed. It manages retries, timeouts, concurrency, and can optionally clear previous messages, swap system messages, and control the use of annotations and rulebooks.

### Method: `direct`

**Signature**:
```python
async def direct(
    self,
    *,
    instruction=None,
    context=None,
    form=None,
    tools=None,
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
    imodel=None,
    system=None,
    rulebook=None,
    directive=None,
    images=None,
    image_path=None,
    **kwargs,
) -> Any:
```

**Parameters**:
- `instruction` (str, optional): Instruction message.
- `context` (Any, optional): Context to perform the instruction on.
- `form` (Form, optional): Form data.
- `tools` (Any, optional): Tools to use.
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
- `imodel` (iModel, optional): Optionally swappable iModel for the commands.
- `system` (str, optional): Optionally swap the system message.
- `rulebook` (Any, optional): The rulebook to use for validation.
- `directive` (str, optional): Directive for the operation.
- `images` (Any, optional): Base64 encoded image content.
- `image_path` (str, optional): Path to image to be read and converted to base64.
- `kwargs`: Additional keyword arguments.

**Return Values**:
- `Any`: The processed response.

**Description**:
Asynchronously directs the operation based on the provided parameters. This method handles a variety of directives and instructions, interacting with tools, models, and validation rules as needed. It manages different parameters for reasoning, prediction, scoring, selection, planning, and more.
