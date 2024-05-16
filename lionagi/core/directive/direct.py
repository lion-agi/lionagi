from .unit.unit import Unit
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
    unit = Unit(branch)

    return await unit.chat(
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
    unit = Unit(branch)

    return await unit.select(
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
    unit = Unit(branch)

    return await unit.predict(
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
    unit = Unit(branch)

    return await unit.act(
        "act",
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
