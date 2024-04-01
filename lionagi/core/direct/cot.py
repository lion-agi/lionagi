from lionagi.libs import convert
from .predict import predict
from .plan import plan
from .react import react
from .utils import _process_tools


async def chain_of_thoughts(
    sentence=None,
    branch=None,
    instruction=None,
    reason=False,
    confidence_score=False,
    num_steps=3,
    directive_kwargs={},
    return_branch=False,
    **kwargs,
):
    """
    Generates a chain of thoughts based on the given sentence, instruction, and number of steps.

    Args:
        sentence (str | None): The input sentence for generating the chain of thoughts.
        branch (Branch | None): The branch to use for generating the chain of thoughts.
        instruction (str | None): The instruction for generating the chain of thoughts.
        reason (bool): Whether to include the reason for each thought in the output (default: False).
        confidence_score (bool): Whether to include the confidence score for each thought in the output (default: False).
        num_steps (int): The number of steps in the chain of thoughts (default: 3).
        directive_kwargs (dict): Additional keyword arguments for the directive functions (default: {}).
        return_branch (bool): Whether to return the branch along with the plan template (default: False).
        **kwargs: Additional keyword arguments for the `plan` function.

    Returns:
        PlanTemplate | tuple[PlanTemplate, Branch]: The plan template with the chain of thoughts, or a tuple of the plan template and the branch if `return_branch` is True.
    """
    out_, outs, answer, reasons, _confidence_score = "", [], "", [], 0
    if branch is not None:
        out_ = await plan(
            sentence,
            branch=branch,
            instruction=instruction,
            num_steps=num_steps,
            **kwargs,
        )
    else:
        out_, branch = await plan(
            sentence,
            instruction=instruction,
            branch=branch,
            num_steps=num_steps,
            return_branch=True,
            **kwargs,
        )

    for i in range(len(out_.plan)):
        _out = await predict(
            branch=branch,
            instruction=out_.plan[f"step_{i + 1}"],
            reason=reason,
            confidence_score=confidence_score,
            **directive_kwargs,
        )
        answer += _out.answer
        if reason:
            reasons.append(_out.reason)
        if confidence_score:
            _confidence_score += _out.confidence_score
        outs.append(_out)

    setattr(out_, "chain_output", outs)
    setattr(out_, "chain_answer", answer)

    if reason:
        setattr(out_, "chain_reasons", reasons)
    if confidence_score:
        setattr(out_, "chain_confidence_score", _confidence_score / len(outs))

    if return_branch:
        return out_, branch

    return out_


async def chain_of_react(
    sentence=None,
    branch=None,
    instruction=None,
    num_steps=3,
    tools=None,
    directive_system=None,
    directive_kwargs={},
    return_branch=False,
    **kwargs,
):
    """
    Generates a chain of reactions based on the given sentence, instruction, number of steps, and tools.

    Args:
        sentence (str | None): The input sentence for generating the chain of reactions.
        branch (Branch | None): The branch to use for generating the chain of reactions.
        instruction (str | None): The instruction for generating the chain of reactions.
        num_steps (int): The number of steps in the chain of reactions (default: 3).
        tools (list | None): The tools to use for generating the reactions.
        directive_system (Any | None): The system configuration for the directive functions.
        directive_kwargs (dict): Additional keyword arguments for the directive functions (default: {}).
        return_branch (bool): Whether to return the branch along with the plan template (default: False).
        **kwargs: Additional keyword arguments for the `plan` function.

    Returns:
        PlanTemplate | tuple[PlanTemplate, Branch]: The plan template with the chain of reactions, or a tuple of the plan template and the branch if `return_branch` is True.
    """
    out_, outs, reasons, actions, action_responses = "", [], [], [], []
    if branch is not None:
        out_ = await plan(
            sentence,
            branch=branch,
            instruction=instruction,
            num_steps=num_steps,
            **kwargs,
        )
    else:
        out_, branch = await plan(
            sentence,
            instruction=instruction,
            branch=branch,
            num_steps=num_steps,
            return_branch=True,
            **kwargs,
        )

    _process_tools(tools, branch)

    for i in range(len(out_.plan)):
        _out = await react(
            branch=branch,
            system=directive_system,
            instruction=out_.plan[f"step_{i + 1}"],
            **directive_kwargs,
        )
        outs.append(_out)
        reasons.append(_out.reason)
        actions.append(_out.actions)
        if _out.action_needed:
            action_responses.append(_out.action_response)

    setattr(out_, "chain_output", convert.to_list(outs))
    setattr(out_, "chain_reason", convert.to_list(reasons))
    setattr(out_, "chain_actions", convert.to_list(actions))
    setattr(out_, "chain_action_response", convert.to_list(action_responses))

    if return_branch:
        return out_, branch

    return out_
