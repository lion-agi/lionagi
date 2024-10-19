import asyncio
from typing import Any

import numpy as np
from lionfuncs import alcall, to_list

from lionagi.core.session.branch import Branch
from lionagi.core.session.session import Session

from ..score.score import score

PROMPT = (
    "Given all items: \n {choices} \n\n Please follow prompt and give score "
    "to the item of interest: \n {item} \n\n"
)


async def rank(
    choices: list[Any],
    num_scorers: int = 5,
    instruction=None,
    context=None,
    system=None,
    reason: bool = False,
    branch: Branch = None,  # branch won't be used for the vote, it is for configuration
    **kwargs,  # additional kwargs for score function
) -> dict:
    session = Session()
    branch = branch or Branch()
    session.change_default_branch(branch)

    async def _score(item):
        b_ = session.new_branch(messages=branch.messages)
        prompt = PROMPT.format(choices=choices, item=item)
        if instruction:
            prompt = f"{instruction}\n\n{prompt} \n\n "

        response = await score(
            score_range=(1, 10),
            instruction=prompt,
            context=context,
            system=system,
            sender=session.ln_id,
            recipient=b_.ln_id,
            precision=1,
            default_score=-1,
            reason=reason,
            **kwargs,
        )

        if response.score == -1:
            return None

        return response

    async def _group_score(item):
        tasks = [asyncio.create_task(_score(item)) for _ in range(num_scorers)]
        responses = await asyncio.gather(*tasks)
        scores = to_list(
            [i.score for i in responses], dropna=True, flatten=True
        )
        return {
            "item": item,
            "scores": scores,
            "average": np.mean(scores) if scores else -1,
        }

    results = await alcall(choices, _group_score)
    return sorted(results, key=lambda x: x["average"], reverse=True)
