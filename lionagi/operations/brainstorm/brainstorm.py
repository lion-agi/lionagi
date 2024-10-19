from lion_core.session.branch import Branch


class BrainstormModel(Operative):

    ideas: list[StepModel] = Field(
        [],
        title="Ideas",
        description="A list of ideas for the next step, generated during brainstorming.",
    )


async def brainstorm(
    num_ideas: int = 3,
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
    response, branch = await _brainstorm(
        num_ideas=num_ideas,
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


async def _brainstorm(
    num_ideas: int = 3,
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    reason: bool = False,
    branch: Branch = None,
    **kwargs,  # additional chat arguments
) -> BrainstormModel | ReasonBrainstormModel:
    prompt = PROMPT.format(num_ideas=num_ideas)
    if instruction:
        prompt = f"{instruction}\n\n{prompt} \n\n "

    branch = branch or Branch()
    response: BrainstormModel | ReasonBrainstormModel | str = (
        await branch.chat(
            instruction=prompt,
            context=context,
            system=system,
            sender=sender,
            recipient=recipient,
            pydantic_model=(
                BrainstormModel if not reason else ReasonBrainstormModel
            ),
            return_pydantic_model=True,
            **kwargs,
        )
    )
    return response, branch
