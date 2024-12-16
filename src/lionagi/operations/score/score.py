# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

import numpy as np
from pydantic import BaseModel

from lionagi.fields.instruct import Instruct
from lionagi.fields.score import SCORES_FIELD
from lionagi.libs.parse.types import to_num
from lionagi.session.types import Branch

from .prompt import PROMPT


class ScoreOperation(BaseModel):
    score: list[float] | float
    response: Any


async def score(
    instruct: Instruct | dict,
    score_range=(1, 10),
    branch: Branch = None,
    num_scores: int = 1,
    use_average: bool = False,
    precision: int = 0,
    default_score=np.nan,
    branch_kwargs: dict[str, Any] | None = None,
    verbose: bool = True,
    return_branch=False,
    **kwargs,
) -> ScoreOperation | tuple[ScoreOperation, Branch]:

    field_models: list = kwargs.get("field_models", [])
    if SCORES_FIELD not in field_models:
        field_models.append(SCORES_FIELD)

    kwargs["field_models"] = field_models
    if branch is None:
        branch = Branch(**(branch_kwargs or {}))

    if isinstance(instruct, Instruct):
        instruct = instruct.to_dict()

    if not isinstance(instruct, dict):
        raise ValueError(
            "instruct needs to be an InstructModel obj or a dictionary of valid parameters"
        )

    guidance = instruct.get("guidance", "")
    instruct["guidance"] = (
        f"\n{PROMPT.format(score_range=score_range, num_scores=num_scores, return_precision=precision)}"
        + guidance
    )

    res = await branch.operate(**instruct, **kwargs)

    return_kind = int if precision == 0 else float
    err = None
    try:
        res.score = [
            to_num(
                i,
                upper_bound=score_range[1],
                lower_bound=score_range[0],
                num_type=return_kind,
                precision=precision,
                num_count=num_scores,
            )
            for i in res.score
        ]
        if use_average:
            scores = res.score
            scores = [scores] if not isinstance(scores, list) else scores
            res.score = np.mean(scores)

        if res.score and num_scores == 1:
            if isinstance(res.score, list):
                res.score = res.score[0]
        if verbose:
            print(f"Score(s): {res.score}")

    except Exception as e:
        err = e
        if verbose:
            print(
                f"Error converting score to {return_kind}: {err}, "
                f"value is set to default: {default_score}"
            )
    res.score = default_score
    out = ScoreOperation(score=res.score, response=res)
    if return_branch:
        return out, branch
    return out
