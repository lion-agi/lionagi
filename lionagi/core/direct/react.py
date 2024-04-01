from lionagi.libs import func_call, AsyncUtil
from pydantic import Field

from ..prompt import ActionTemplate
from ..branch import Branch

from .utils import _process_tools


class ReactTemplate(ActionTemplate):
    """
    A template for generating a reaction based on a given sentence and instruction.

    Attributes:
        template_name (str): The name of the template. Default is "default_react".
        sentence (str | list | dict | None): The given sentence(s) to reason and take actions on.

    Args:
        sentence (str | list | dict | None): The given sentence(s) to reason and take actions on.
        instruction (str | None): The instruction for the reaction.
        confidence_score (bool): Whether to include the confidence score in the output fields.
        **kwargs: Additional keyword arguments.
    """

    template_name: str = "default_react"
    sentence: str | list | dict | None = Field(
        default_factory=str,
        description="the given sentence(s) to reason and take actions on",
    )

    def __init__(
        self,
        sentence=None,
        instruction=None,
        confidence_score=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.sentence = sentence
        self.task = f"Think step by step. Perform reasoning and prepare actions with given tools only.Instruction: {instruction}. Absolutely DO NOT MAKE UP FUNCTIONS !!!"

        if confidence_score:
            self.output_fields.append("confidence_score")


async def _react(
    sentence=None,
    *,
    instruction=None,
    branch=None,
    confidence_score=False,
    retries=2,
    delay=0.5,
    backoff_factor=2,
    default_value=None,
    timeout=None,
    branch_name=None,
    system=None,
    messages=None,
    service=None,
    sender=None,
    llmconfig=None,
    tools=None,
    datalogger=None,
    persist_path=None,
    tool_manager=None,
    return_branch=False,
    **kwargs,
):
    """
    Generate a reaction based on the given sentence and instruction.

    Args:
        sentence (str | None): The given sentence to reason and take actions on.
        instruction (str | None): The instruction for the reaction.
        branch (Branch | None): The branch to use for the reaction.
        confidence_score (bool): Whether to include the confidence score in the output fields.
        retries (int): The number of retries for failed actions.
        delay (float): The delay between retries in seconds.
        backoff_factor (float): The backoff factor for increasing the delay between retries.
        default_value (Any | None): The default value to return if the reaction fails.
        timeout (float | None): The timeout for the reaction in seconds.
        branch_name (str | None): The name of the branch.
        system (Any | None): The system configuration for the branch.
        messages (list | None): The initial messages for the branch.
        service (Any | None): The service to use for the branch.
        sender (Any | None): The sender of the reaction.
        llmconfig (Any | None): The LLM configuration for the branch.
        tools (list | None): The tools to use for the reaction.
        datalogger (Any | None): The data logger for the branch.
        persist_path (str | None): The path to persist the branch data.
        tool_manager (Any | None): The tool manager for the branch.
        return_branch (bool): Whether to return the branch along with the reaction template.
        **kwargs: Additional keyword arguments.

    Returns:
        ReactTemplate | tuple: The reaction template if `return_branch` is False, or a tuple of the reaction template and the branch if `return_branch` is True.
    """

    if "temperature" not in kwargs:
        kwargs["temperature"] = 0.1

    instruction = instruction or ""

    if branch and tools:
        _process_tools(tools, branch)

    branch = branch or Branch(
        name=branch_name,
        system=system,
        messages=messages,
        service=service,
        sender=sender,
        llmconfig=llmconfig,
        tools=tools,
        datalogger=datalogger,
        persist_path=persist_path,
        tool_manager=tool_manager,
    )

    _template = ReactTemplate(
        sentence=sentence,
        instruction=instruction,
        confidence_score=confidence_score,
    )

    await func_call.rcall(
        branch.chat,
        prompt_template=_template,
        retries=retries,
        delay=delay,
        backoff_factor=backoff_factor,
        default=default_value,
        timeout=timeout,
        **kwargs,
    )

    if _template.action_needed:
        actions = _template.actions
        tasks = [branch.tool_manager.invoke(i.values()) for i in actions]
        results = await AsyncUtil.execute_tasks(*tasks)

        a = []
        for idx, item in enumerate(actions):
            res = {
                "function": item["function"],
                "arguments": item["arguments"],
                "output": results[idx],
            }
            branch.add_message(response=res)
            a.append(res)

        _template.__setattr__("action_response", a)

    return (_template, branch) if return_branch else _template


async def react(
    sentence=None,
    *,
    instruction=None,
    num_instances=1,
    branch=None,
    confidence_score=False,
    retries=2,
    delay=0.5,
    backoff_factor=2,
    default_value=None,
    timeout=None,
    branch_name=None,
    system=None,
    messages=None,
    service=None,
    sender=None,
    llmconfig=None,
    tools=None,
    datalogger=None,
    persist_path=None,
    tool_manager=None,
    return_branch=False,
    **kwargs,
):
    """
    Generate one or more reactions based on the given sentence and instruction.

    Args:
        sentence (str | None): The given sentence to reason and take actions on.
        instruction (str | None): The instruction for the reaction.
        num_instances (int): The number of reaction instances to generate.
        branch (Branch | None): The branch to use for the reaction.
        confidence_score (bool): Whether to include the confidence score in the output fields.
        retries (int): The number of retries for failed actions.
        delay (float): The delay between retries in seconds.
        backoff_factor (float): The backoff factor for increasing the delay between retries.
        default_value (Any | None): The default value to return if the reaction fails.
        timeout (float | None): The timeout for the reaction in seconds.
        branch_name (str | None): The name of the branch.
        system (Any | None): The system configuration for the branch.
        messages (list | None): The initial messages for the branch.
        service (Any | None): The service to use for the branch.
        sender (Any | None): The sender of the reaction.
        llmconfig (Any | None): The LLM configuration for the branch.
        tools (list | None): The tools to use for the reaction.
        datalogger (Any | None): The data logger for the branch.
        persist_path (str | None): The path to persist the branch data.
        tool_manager (Any | None): The tool manager for the branch.
        return_branch (bool): Whether to return the branch along with the reaction template.
        **kwargs: Additional keyword arguments.

    Returns:
        ReactTemplate | list | tuple: The reaction template if `num_instances` is 1, a list of reaction templates if `num_instances` is greater than 1, or a tuple of the reaction template(s) and the branch if `return_branch` is True.
    """

    async def _inner(i=0):
        return await _react(
            sentence=sentence,
            instruction=instruction,
            num_instances=num_instances,
            branch=branch,
            confidence_score=confidence_score,
            retries=retries,
            delay=delay,
            backoff_factor=backoff_factor,
            default_value=default_value,
            timeout=timeout,
            branch_name=branch_name,
            system=system,
            messages=messages,
            service=service,
            sender=sender,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            tool_manager=tool_manager,
            return_branch=return_branch,
            **kwargs,
        )

    if num_instances == 1:
        return await _inner()

    elif num_instances > 1:
        return await func_call.alcall(range(num_instances), _inner)
