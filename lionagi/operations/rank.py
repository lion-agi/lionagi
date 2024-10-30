import asyncio
from typing import Any

import numpy as np
from lion_core.session.branch import Branch
from lion_core.session.session import Session
from lion_service import iModel
from lionfuncs import alcall, to_list

from .config import DEFAULT_CHAT_CONFIG
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
    tools: Any = None,
    imodel: iModel = None,
    branch: Branch = None,  # branch won't be used for the vote, it is for configuration
    clear_messages: bool = False,
    system_sender=None,
    system_datetime=None,
    num_parse_retries: int = 0,
    retry_imodel: iModel = None,
    return_session: bool = False,
    **kwargs,  # additional kwargs for score function
) -> dict:

    if branch and branch.imodel:
        imodel = imodel or branch.imodel
    else:
        imodel = imodel or iModel(**DEFAULT_CHAT_CONFIG)

    branch = branch or Branch(imodel=imodel)
    session = Session(default_branch=branch)

    async def _score(item):
        async with session.branches.async_lock:
            b_ = session.new_branch(messages=session.default_branch.messages)

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
            system_datetime=system_datetime,
            system_sender=system_sender,
            sender=session.ln_id,
            recipient=b_.ln_id,
            default_score=-1,
            reason=reason,
            actions=actions,
            tools=tools,
            clear_messages=clear_messages,
            num_parse_retries=num_parse_retries,
            retry_imodel=retry_imodel,
            **kwargs,
        )

        if response.score == -1:
            return None

        return response

    async def _group_score(item):
        tasks = [asyncio.create_task(_score(item)) for _ in range(num_scorers)]
        responses = await asyncio.gather(*tasks)
        responses = [i for i in responses if i is not None]
        scores = to_list(
            [i.score for i in responses], dropna=True, flatten=True
        )
        return {
            "item": item,
            "scores": scores,
            "average": np.mean(scores) if scores else -1,
        }

    results = await alcall(choices, _group_score)
    results = sorted(results, key=lambda x: x["average"], reverse=True)
    if return_session:
        return results, session
    return results
