import logging

import numpy as np
from lionfuncs import to_num
from pydantic import BaseModel, Field, field_validator

from lionagi.core.session.branch import Branch


class ScoreModel(BaseModel):

    score: list[float] | float = Field(
        default_factory=list,
        description="** A numeric score or a list of numeric scores.**",
    )

    @field_validator("score", mode="before")
    def validate_score(cls, value) -> list:
        return [value] if not isinstance(value, list) else value


PROMPT = "Please follow prompt and provide {num_scores} numeric score(s) in {score_range} for the given context. Return as {return_precision} format"


async def score(
    score_range=(1, 10),
    instruction=None,
    guidance=None,
    context=None,
    system=None,
    reason: bool = False,
    actions: bool = False,
    tools=None,
    branch: Branch = None,
    sender=None,
    recipient=None,
    progress=None,
    clear_messages: bool = False,
    system_sender: str = None,
    system_datetime: str | bool = None,
    return_branch: bool = False,
    invoke_action: bool = True,
    num_scores: int = 1,
    use_average: bool = False,
    precision: int = 0,
    default_score=np.nan,
    **kwargs,
) -> ScoreModel:
    branch = branch or Branch()

    return_precision = "integer" if precision == 0 else f"num:{precision}f"
    prompt = PROMPT.format(
        num_scores=num_scores,
        score_range=score_range,
        return_precision=return_precision,
    )
    if instruction:
        prompt = f"{instruction}\n\n{prompt} \n\n "

    if system:
        branch.add_message(
            system=system,
            system_datetime=system_datetime,
            sender=system_sender,
        )

    response = await branch.operate(
        instruction=instruction,
        guidance=guidance,
        context=(
            [{"operation": prompt}, context]
            if context
            else {"operation": prompt}
        ),
        sender=sender,
        recipient=recipient,
        reason=reason,
        actions=actions,
        tools=tools,
        progress=progress,
        clear_messages=clear_messages,
        operative_model=ScoreModel,
        invoke_action=invoke_action,
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
        if num_scores == 1:
            response.score = response.score[0]
    except Exception as e:
        logging.error(
            f"Error converting score to {return_kind}: {e}, "
            f"value is set to default: {default_score}"
        )
        response.score = default_score

    if return_branch:
        return response, branch
    return response
