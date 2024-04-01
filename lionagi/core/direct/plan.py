"""
This module contains the PlanTemplate class for generating a step-by-step plan based on a given sentence or context.

The PlanTemplate class is a subclass of ScoredTemplate and provides functionality for generating a plan using a language model.
It includes fields for the input sentence, instruction, generated plan, confidence score, and reason for the plan.

The module also provides a `plan` function that uses the PlanTemplate to generate a plan based on the given sentence and instruction.
"""

from lionagi.libs import func_call, ParseUtil
from pydantic import Field

from ..prompt import ScoredTemplate
from ..branch import Branch


class PlanTemplate(ScoredTemplate):
    """
    A class for generating a step-by-step plan based on a given sentence or context.

    Attributes:
        template_name (str): The name of the plan template (default: "default_plan").
        sentence (str | list | dict): The given sentence(s) or context to generate a plan for.
        plan (dict | str): The generated step-by-step plan, returned as a dictionary following the format {step_n: {plan: ..., reason: ...}}.
        signature (str): The signature indicating the input and output fields (default: "sentence -> plan").

    Args:
        sentence (str | list | dict | None): The given sentence(s) or context to generate a plan for.
        instruction (str | None): The instruction for generating the plan.
        confidence_score (bool): Whether to include the confidence score in the output (default: False).
        reason (bool): Whether to include the reason for the plan in the output (default: False).
        num_step (int): The number of steps in the generated plan (default: 3).
        **kwargs: Additional keyword arguments.
    """

    template_name: str = "default_plan"
    sentence: str | list | dict = Field(
        default_factory=str,
        description="the given sentence(s) or context to generate a plan for",
    )
    plan: dict | str = Field(
        default_factory=dict,
        description="the generated step by step plan, return as a dictionary following {step_n: {plan: ..., reason: ...}} format",
    )
    signature: str = "sentence -> plan"

    def __init__(
        self,
        sentence=None,
        instruction=None,
        confidence_score=False,
        reason=False,
        num_step=3,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.sentence = sentence
        self.task = f"Generate a {num_step}_step plan based on the given context. Instruction: {instruction}."

        if reason:
            self.output_fields.append("reason")

        if confidence_score:
            self.output_fields.append("confidence_score")


async def _plan(
    sentence,
    *,
    instruction=None,
    branch=None,
    confidence_score=False,
    reason=False,
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
    Generates a step-by-step plan based on the given sentence and instruction using a language model.

    Args:
        sentence (str | list | dict): The given sentence(s) or context to generate a plan for.
        instruction (str | None): The instruction for generating the plan.
        branch (Branch | None): The branch to use for generating the plan.
        confidence_score (bool): Whether to include the confidence score in the output (default: False).
        reason (bool): Whether to include the reason for the plan in the output (default: False).
        retries (int): The number of retries for the API call (default: 2).
        delay (float): The initial delay between retries in seconds (default: 0.5).
        backoff_factor (float): The backoff factor for exponential delay between retries (default: 2).
        default_value (Any | None): The default value to return if the API call fails (default: None).
        timeout (float | None): The timeout for the API call in seconds (default: None).
        branch_name (str | None): The name of the branch to use for generating the plan.
        system (Any | None): The system configuration for the branch.
        messages (Any | None): The messages to initialize the branch with.
        service (Any | None): The service to use for generating the plan.
        sender (str | None): The sender of the plan generation request.
        llmconfig (Any | None): The configuration for the language model.
        tools (Any | None): The tools to use for generating the plan.
        datalogger (Any | None): The data logger for the branch.
        persist_path (str | None): The path to persist the branch data.
        tool_manager (Any | None): The tool manager for the branch.
        return_branch (bool): Whether to return the branch along with the plan template (default: False).
        **kwargs: Additional keyword arguments for the API call.

    Returns:
        PlanTemplate | tuple[PlanTemplate, Branch]: The plan template with the generated plan, or a tuple of the plan template and the branch if `return_branch` is True.
    """
    if "temperature" not in kwargs:
        kwargs["temperature"] = 0.1

    instruction = instruction or ""

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

    _template = PlanTemplate(
        sentence=sentence,
        instruction=instruction,
        confidence_score=confidence_score,
        reason=reason,
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

    _template.plan = ParseUtil.fuzzy_parse_json(_template.plan)

    return (_template, branch) if return_branch else _template


async def plan(
    sentence,
    *,
    instruction=None,
    num_instances=1,
    branch=None,
    confidence_score=False,
    reason=False,
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
    Generates one or more step-by-step plans based on the given sentence and instruction using a language model.

    Args:
        sentence (str | list | dict): The given sentence(s) or context to generate a plan for.
        instruction (str | None): The instruction for generating the plan.
        num_instances (int): The number of plan instances to generate (default: 1).
        branch (Branch | None): The branch to use for generating the plan.
        confidence_score (bool): Whether to include the confidence score in the output (default: False).
        reason (bool): Whether to include the reason for the plan in the output (default: False).
        retries (int): The number of retries for the API call (default: 2).
        delay (float): The initial delay between retries in seconds (default: 0.5).
        backoff_factor (float): The backoff factor for exponential delay between retries (default: 2).
        default_value (Any | None): The default value to return if the API call fails (default: None).
        timeout (float | None): The timeout for the API call in seconds (default: None).
        branch_name (str | None): The name of the branch to use for generating the plan.
        system (Any | None): The system configuration for the branch.
        messages (Any | None): The messages to initialize the branch with.
        service (Any | None): The service to use for generating the plan.
        sender (str | None): The sender of the plan generation request.
        llmconfig (Any | None): The configuration for the language model.
        tools (Any | None): The tools to use for generating the plan.
        datalogger (Any | None): The data logger for the branch.
        persist_path (str | None): The path to persist the branch data.
        tool_manager (Any | None): The tool manager for the branch.
        return_branch (bool): Whether to return the branch along with the plan template(s) (default: False).
        **kwargs: Additional keyword arguments for the API call.

    Returns:
        PlanTemplate | list[PlanTemplate] | tuple[PlanTemplate | list[PlanTemplate], Branch]: The plan template(s) with the generated plan(s), or a tuple of the plan template(s) and the branch if `return_branch` is True.
    """

    async def _inner(i=0):
        return await _plan(
            sentence=sentence,
            instruction=instruction,
            branch=branch,
            confidence_score=confidence_score,
            reason=reason,
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
