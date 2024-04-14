
### Class: `BranchFlowMixin`

An abstract base class that provides flow-based methods for branches.

#### Methods:
##### `async chat`
`(self, instruction: Union[Instruction, str] = None, context: Optional[Any] = None, sender: Optional[str] = None, system: Optional[Union[System, str, dict[str, Any]]] = None, tools: TOOL_TYPE = False, out: bool = True, invoke: bool = True, output_fields=None, prompt_template=None, **kwargs) -> Any`
Performs a chat flow in the branch.

Parameters:
- `instruction` (`Union[Instruction, str] | None`): The instruction for the chat (optional).
- `context` (`Optional[Any]`): The context for the chat (optional).
- `sender` (`Optional[str]`): The sender of the chat (optional).
- `system` (`Optional[Union[System, str, dict[str, Any]]]`): The system message for the chat (optional).
- `tools` (`TOOL_TYPE`): The tools to use in the chat (default: `False`).
- `out` (`bool`): Whether to output the result (default: `True`).
- `invoke` (`bool`): Whether to invoke the chat (default: `True`).
- `output_fields` (`Any`): The output fields for the chat (`optional`).
- `prompt_template` (`Any`): The prompt template for the chat (`optional`).
- `**kwargs`: Additional keyword arguments.

Returns:
`Any`: The result of the chat flow.

##### `async ReAct`
`(self, instruction: Instruction | str | dict[str, dict | str], context=None, sender=None, system=None, tools=None, auto=False, num_rounds: int = 1, reason_prompt=None, action_prompt=None, output_prompt=None, **kwargs) -> Any`
Performs a ReAct flow in the branch.

Parameters:
- `instruction` (`Instruction | str | dict[str, dict | str]`): The instruction for the ReAct flow.
- `context` (Any): The context for the ReAct flow (optional).
- `sender` (Any): The sender of the ReAct flow (optional).
- `system` (Any): The system message for the ReAct flow (optional).
- `tools` (Any): The tools to use in the ReAct flow (optional).
- `auto` (bool): Whether to automatically perform the ReAct flow (default: False).
- `num_rounds` (int): The number of rounds for the ReAct flow (default: 1).
- `reason_prompt` (Any): The reasoning prompt for the ReAct flow (optional).
- `action_prompt` (Any): The action prompt for the ReAct flow (optional).
- `output_prompt` (Any): The output prompt for the ReAct flow (optional).
- `**kwargs`: Additional keyword arguments.

Returns:
`Any`: The result of the ReAct flow.

##### `async followup`
`(self, instruction: Instruction | str | dict[str, dict | str], context=None, sender=None, system=None, tools=None, max_followup: int = 1, auto=False, followup_prompt=None, output_prompt=None, out=True, **kwargs) -> Any`
Performs a followup flow in the branch.

Parameters:
- `instruction` (`Instruction | str | dict[str, dict | str]`): The instruction for the followup flow.
- `context` (Any): The context for the followup flow (optional).
- `sender` (Any): The sender of the followup flow (optional).
- `system` (Any): The system message for the followup flow (optional).
- `tools` (Any): The tools to use in the followup flow (optional).
- `max_followup` (int): The maximum number of followups (default: 1).
- `auto` (bool): Whether to automatically perform the followup flow (default: False).
- `followup_prompt` (Any): The followup prompt for the flow (optional).
- `output_prompt` (Any): The output prompt for the flow (optional).
- `out` (bool): Whether to output the result (default: True).
- `**kwargs`: Additional keyword arguments.

Returns:
`Any`: The result of the followup flow.
