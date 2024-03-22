from .select import select
from .score import score


async def sentiment(
    context,
    choices=None,
    instruction=None,
    score_range=(0, 1),
    inclusive=True,
    num_digit=2,
    reason=False,
    method="llm",
    objective=None,
    default_key="answer",
    retries=2,
    to_type="str",
    **kwargs,
):
    if to_type == "str":
        if choices is None:
            choices = ["positive", "negative", "neutral"]

        if objective is None:
            objective = "classify sentiment"

        return await select(
            context=context,
            choices=choices,
            method=method,
            objective=objective,
            default_key=default_key,
            retries=retries,
            reason=reason,
            out_str=True,
            **kwargs,
        )

    elif to_type == "num":
        return await score(
            context=context,
            instruction=instruction,
            score_range=score_range,
            inclusive=inclusive,
            num_digit=num_digit,
            reason=reason,
            method=method,
            default_key=default_key,
            retries=retries,
            **kwargs,
        )
