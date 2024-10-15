import logging

import numpy as np
from lionfuncs import to_num

from lionagi.core.session.branch import Branch

from .models.score_model import ReasonScoreModel, ScoreModel

PROMPT = "Please follow prompt and provide {num_scores} numeric score(s) in {score_range} for the given context. Return as {return_precision} format"


async def score(
    score_range=(1, 10),
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    reason: bool = False,
    branch: Branch = None,
    return_branch=False,
    num_scores=1,
    use_average: bool = False,
    precision: int = 0,
    default_score=np.nan,
    **kwargs,  # additional chat arguments
):

    response, branch = await _score(
        score_range=score_range,
        instruction=instruction,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        reason=reason,
        branch=branch,
        num_scores=num_scores,
        use_average=use_average,
        precision=precision,
        default_score=default_score,
        **kwargs,
    )
    if return_branch:
        return response, branch
    return response


async def _score(
    score_range=(1, 10),
    instruction=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    reason: bool = False,
    branch: Branch = None,
    num_scores=1,
    use_average: bool = False,
    precision: int = 0,
    default_score=np.nan,
    **kwargs,  # additional chat arguments
) -> ScoreModel | ReasonScoreModel:
    return_precision = "integer" if precision == 0 else f"num:{precision}f"
    prompt = PROMPT.format(
        num_scores=num_scores,
        score_range=score_range,
        return_precision=return_precision,
    )
    if instruction:
        prompt = f"{instruction}\n\n{prompt} \n\n "

    branch = branch or Branch()
    response: ScoreModel | ReasonScoreModel = await branch.chat(
        instruction=prompt,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        pydantic_model=ScoreModel if not reason else ReasonScoreModel,
        return_pydantic_model=True,
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
        if use_average:
            response.score = np.mean(response.score)
    except Exception as e:
        logging.error(
            f"Error converting score to {return_kind}: {e}, "
            f"value is set to default: {default_score}"
        )
        response.score = default_score

    return response, branch
