"""
This module contains the vote function for generating and scoring multiple outputs and selecting the top-ranked ones.

The vote function generates multiple outputs using a specified directive function (default: predict), scores each output
using the score function, and returns the top-ranked output(s) based on the scores. It allows for customization of the
number of generations, number of outputs to return, number of scorers, score range, and scorer instruction.
"""

from lionagi.libs import func_call

from .predict import predict
from .score import score


async def vote(
    sentence,
    directive=predict,
    score_field="answer",
    num_generations=5,
    num_output=1,
    num_scorer=5,
    score_range=(0, 100),
    num_digit=2,
    scorer_instruction=None,
    **kwargs,
):

    async def _inner(i):
        out_ = await directive(sentence, **kwargs)
        score_ = await score(
            getattr(out_, score_field),
            context=sentence,
            instruction=scorer_instruction,
            score_range=score_range,
            num_digit=num_digit,
            num_instances=num_scorer,
            return_template=False,
        )

        out_.__setattr__("score", score_)
        return out_

    _outs = await func_call.alcall(list(range(num_generations)), _inner)

    from numpy import argsort as _argsort, array as _array

    top_index = _argsort([i.score for i in _outs])[-num_output:]
    final_output = list(_array(_outs)[top_index])

    return final_output[0] if len(final_output) == 1 else final_output
