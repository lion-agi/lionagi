import asyncio
from typing import Any

import numpy as np
from lionfuncs import alcall, to_list

from lionagi.core.session.branch import Branch
from lionagi.core.session.session import Session

from .score import score

PROMPT = (
    "Given all items: \n {choices} \n\n Please follow prompt and give score "
    "to the item of interest: \n {item} \n\n"
)


async def rank(
    choices: list[Any],
    num_scorers: int = 5,
    instruction=None,
    guidance=None,
    context=None,
    system=None,
    reason: bool = False,
    actions: bool = False,
    tools=None,
    branch: Branch = None,  # branch won't be used for the vote, it is for configuration
    invoke_action: bool = True,
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

        kwargs["branch"] = b_
        kwargs["score_range"] = kwargs.get("score_range", (1, 10))
        kwargs["num_scores"] = kwargs.get("num_scores", 1)
        kwargs["precision"] = kwargs.get("precision", 1)

        response = await score(
            instruction=prompt,
            guidance=guidance,
            context=context,
            system=system,
            sender=session.ln_id,
            recipient=b_.ln_id,
            default_score=-1,
            reason=reason,
            actions=actions,
            invoke_action=invoke_action,
            tools=tools,
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
