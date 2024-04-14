## MonoReAct Class
A specialized class designed for handling sequences of reasoning and action tasks with an LLM. It extends the `MonoChat` class and integrates the capability to process instructions, system messages, and invoke tools dynamically during the conversation.

### Attributes
- **REASON_PROMPT (str)**: Default prompt used to guide the LLM during reasoning tasks.
- **ACTION_PROMPT (str)**: Default prompt used to guide the LLM during action tasks.
- **OUTPUT_PROMPT (str)**: Default prompt used for presenting the final output to the user.

### Methods

#### __init__
Initializes the `MonoReAct` instance with a specific branch.
- **Parameters**:
  - `branch`: The `Branch` instance associated with the reasoning and action operations.
- **Returns**:
  - None

#### ReAct
Conducts a series of reasoning and action steps with an LLM based on provided instructions, optionally using various tools.
- **Parameters**:
  - `instruction (Instruction | str | dict)`: Detailed instructions for the reasoning and action tasks.
  - `context (Optional[Any])`: Additional context for the tasks.
  - `sender (Optional[str])`: Identifier for the sender of the message.
  - `system (Optional[Any])`: System message to process.
  - `tools (Optional[Any])`: Specifies the tools to be invoked during the tasks.
  - `num_rounds (int)`: The number of reasoning and action rounds to perform.
  - `reason_prompt (Optional[str])`: Custom prompt for reasoning steps.
  - `action_prompt (Optional[str])`: Custom prompt for action steps.
  - `output_prompt (Optional[str])`: Custom prompt for presenting the final output.
  - `**kwargs`: Additional keyword arguments for the tasks.
- **Returns**:
  - The result of the reasoning and action steps.

#### _get_prompt
Generates the appropriate prompt for a reasoning or action step based on provided parameters.
- **Parameters**:
  - `prompt (Optional[str])`: Specific prompt for the step.
  - `default (Optional[str])`: Default prompt if no specific prompt is provided.
  - `num_steps (Optional[int])`: Remaining number of steps in the task.
  - `instruction (Optional[Any])`: Original user instruction.
- **Returns**:
  - `str`: The generated prompt for the reasoning or action step.

#### _create_followup_config
Creates configuration settings for the follow-up tasks, considering the provided tools and parameters.
- **Parameters**:
  - `tools (Optional[Any])`: Tools to be invoked during the tasks.
  - `tool_choice (str)`: Strategy for tool selection.
  - `**kwargs`: Additional configuration settings.
- **Returns**:
  - `dict`: Configuration for the follow-up tasks.
- **Raises**:
  - `ValueError`: If no tools are registered or found.

#### _ReAct
Executes the actual reasoning and action tasks, managing the sequence based on user inputs and system configurations.
- **Parameters**:
  - Same as `ReAct` method.
- **Returns**:
  - Optional[str]: The result of the reasoning and action tasks, if `out` is True.

### Usage Example
```python
# Assuming 'branch' is a pre-configured Branch instance
mono_react = MonoReAct(branch)
result = await mono_react.ReAct(
    instruction="Further details on user preferences?",
    num_rounds=3,
    tools=True,
    out=True,
    invoke=True
)
