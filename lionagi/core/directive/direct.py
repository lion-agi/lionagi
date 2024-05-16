from ..session.branch import Branch


async def chat(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    **kwargs,
):
    branch = branch or Branch()
    from .unit.base import Chat

    directive = Chat(branch)
    return await directive.chat(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        branch=branch,
        **kwargs,
    )


async def select(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    choices=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    **kwargs,
):
    branch = branch or Branch()
    from .unit.select import Select

    directive = Select(branch)

    return await directive.select(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        choices=choices,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        **kwargs,
    )


async def plan(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    choices=None,
    branch=None,
    form=None,
    num_step=3,
    confidence_score=None,
    reason=False,
    **kwargs,
):
    branch = branch or Branch()
    from .unit.plan import Plan

    directive = Plan(branch)

    return await directive.plan(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        choices=choices,
        form=form,
        num_step=num_step,
        confidence_score=confidence_score,
        reason=reason,
        **kwargs,
    )


async def predict(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    **kwargs,
):
    branch = branch or Branch()
    from .unit.predict import Predict

    directive = Predict(branch)
    if system:
        branch.add_message(system=system)

    return await directive.direct(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        **kwargs,
    )


async def act(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    **kwargs,
):
    branch = branch or Branch()
    return await branch.direct(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        **kwargs,
    )


async def score(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence_score=None,
    reason=False,
    **kwargs,
):
    branch = branch or Branch()
    return await branch.direct(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence_score=confidence_score,
        reason=reason,
        **kwargs,
    )
