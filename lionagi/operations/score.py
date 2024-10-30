import logging
from typing import Any

import numpy as np
from lion_core.session.branch import Branch
from lion_service import iModel
from lionfuncs import to_num
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .config import DEFAULT_CHAT_CONFIG

PROMPT = "Please follow prompt and provide {num_scores} numeric score(s) in {score_range} for the given context. Return as {return_precision} format"


class ScoreModel(BaseModel):

    score: list | float = Field(
        default_factory=list,
        description="** A numeric score or a list of numeric scores.**",
    )

    model_config = ConfigDict(
        population_by_field_name=True,
        arbitrary_types_allowed=True,
    )

    @field_validator("score", mode="before")
    def validate_score(cls, value) -> list:
        return [value] if not isinstance(value, list) else value


async def score(
    score_range=(1, 10),
    instruction=None,
    guidance=None,
    context=None,
    system=None,
    reason: bool = False,
    actions: bool = False,
    tools: Any = None,
    imodel: iModel = None,
    branch: Branch = None,
    sender=None,
    recipient=None,
    clear_messages: bool = False,
    system_sender=None,
    system_datetime=None,
    return_branch=False,
    num_parse_retries: int = 0,
    retry_imodel: iModel = None,
    num_scores: int = 1,
    use_average: bool = False,
    precision: int = 0,
    default_score=np.nan,
    **kwargs,
) -> ScoreModel:

    if branch and branch.imodel:
        imodel = imodel or branch.imodel
    else:
        imodel = imodel or iModel(**DEFAULT_CHAT_CONFIG)

    branch = branch or Branch(imodel=imodel)

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

    _context = [{"operation": prompt}]
    if context:
        _context.append(context)

    kwargs["frozen"] = False
    response = await branch.operate(
        instruction=instruction,
        guidance=guidance,
        context=_context,
        sender=sender,
        recipient=recipient,
        reason=reason,
        actions=actions,
        tools=tools,
        clear_messages=clear_messages,
        operative_model=ScoreModel,
        imodel=imodel,
        retry_imodel=retry_imodel,
        num_parse_retries=num_parse_retries,
        **kwargs,
    )

    return_kind = int if precision == 0 else float
    err = None
    try:
        if isinstance(response, dict):
            response = ScoreModel(**response)

        response.score = [
            to_num(
                i,
                upper_bound=score_range[1],
                lower_bound=score_range[0],
                num_type=return_kind,
                precision=precision,
                num_count=num_scores,
            )
            for i in response.score
        ]
        if use_average:
            scores = response.score
            scores = [scores] if not isinstance(scores, list) else scores
            response.score = np.mean(scores)

        if response.score and num_scores == 1:
            if isinstance(response.score, list):
                response.score = response.score[0]

        if return_branch:
            return response, branch
        return response

    except Exception as e:
        err = e
        pass

    logging.error(
        f"Error converting score to {return_kind}: {err}, "
        f"value is set to default: {default_score}"
    )
    response.score = default_score
    if return_branch:
        return response, branch
    return response
