async def score(
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    branch=None,
    form=None,
    confidence=None,
    num_digits=None,
    score_range=None,
    image: str | list[str] | None = None,
    verbose=True,
    reason=False,
    reflect=None,
    **kwargs,
):
    from lionagi.os.operator.processor.unit.unit import UnitProcessor

    unit = UnitProcessor(branch)
    return await unit.direct(
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        form=form,
        confidence=confidence,
        reason=reason,
        score_range=score_range,
        num_digits=num_digits,
        image=image,
        verbose_direct=verbose,
        reflect=reflect,
        **kwargs,
    )
