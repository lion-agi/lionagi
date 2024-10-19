import logging
from typing import Literal

import numpy as np
from lionfuncs import to_num
from pydantic import field_validator

from lionagi.core.operative.operative import Operative
from lionagi.core.session.branch import Branch

from .prompt import PROMPT


class ScoreModel(Operative):
    score: list[float] | float = []

    @field_validator("score", mode="before")
    def validate_score(cls, value) -> list:
        return [value] if not isinstance(value, list) else value


async def score(
    score_range=(1, 10),
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    tools=None,
    reason: bool = False,
    actions: bool = False,
    invoke_action: bool = True,
    max_num_actions: int | Literal["auto"] = "auto",
    branch=None,
    return_branch=False,
    num_scores=1,
    use_average: bool = False,
    precision: int = 0,
    default_score=np.nan,
    **kwargs,
):
    return_precision = "integer" if precision == 0 else f"num:{precision}f"
    prompt = PROMPT.format(
        num_scores=num_scores,
        score_range=score_range,
        return_precision=return_precision,
    )
    if instruction:
        prompt = f"{instruction}\n\n{prompt} \n\n "

    branch = branch or Branch()

    response = await branch.operate(
        operative=ScoreModel,
        intruction=prompt,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        tools=tools,
        reason=reason,
        actions=actions,
        invoke_action=invoke_action,
        max_num_actions=max_num_actions,
        **kwargs,
    )
    return_kind = int if precision == 0 else float
    try:
        response.score = [
            to_num(
                i,
                upper_bound=score_range[1],
                lower_bound=score_range[0],
                num_type=return_kind,
                precision=precision if precision != 0 else None,
                num_count=num_scores,
            )
            for i in response.score
        ]
        if len(response.score) == 1:
            response.score = response.score[0]
        if use_average:
            response.score = np.mean(response.score)
    except Exception as e:
        logging.error(
            f"Error converting score to {return_kind}: {e}, "
            f"value is set to default: {default_score}"
        )
        response.score = default_score

    if return_branch:
        return response, branch
    return response
