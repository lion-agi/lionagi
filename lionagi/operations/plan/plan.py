from lionagi.core.session.branch import Branch

from .plan_model import PlanModel, ReasonPlanModel

PROMPT = (
    "Please follow prompt and provide step-by-step plan of {num_steps} steps"
)


async def plan(
    num_steps: int = 3,
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    reason: bool = False,
    branch: Branch = None,
    return_branch=False,
    **kwargs,  # additional chat arguments
):
    response, branch = await _plan(
        num_steps=num_steps,
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        reason=reason,
        branch=branch,
        **kwargs,
    )
    if return_branch:
        return response, branch
    return response


async def _plan(
    num_steps: int = 3,
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    reason: bool = False,
    branch: Branch = None,
    **kwargs,  # additional chat arguments
) -> PlanModel | ReasonPlanModel:
    prompt = PROMPT.format(num_steps=num_steps)
    if instruction:
        prompt = f"{instruction}\n\n{prompt} \n\n "

    branch = branch or Branch()
    response: PlanModel | ReasonPlanModel = await branch.chat(
        instruction=prompt,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        pydantic_model=PlanModel if not reason else ReasonPlanModel,
        return_pydantic_model=True,
        **kwargs,
    )
    return response, branch
