from lionagi.libs import func_call, convert
from ..branch import Branch
from .utils import _handle_single_out


async def score(
    context,
    instruction=None,
    *,
    score_range=(1, 10),
    inclusive=True,
    num_digit=0,
    default_key="score",
    method="llm",
    reason=False,
    confidence_score=False,
    retry_kwargs=None,
    **kwargs,
):
    if retry_kwargs is None:
        retry_kwargs = {}
    return await _force_score(
        context=context,
        instruction=instruction,
        score_range=score_range,
        inclusive=inclusive,
        num_digit=num_digit,
        default_key=default_key,
        method=method,
        reason=reason,
        confidence_score=confidence_score,
        retry_kwargs=retry_kwargs,
        **kwargs,
    )


async def _force_score(
    context,
    instruction=None,
    score_range=(1, 10),
    inclusive=True,
    num_digit=1,
    default_key="score",
    method="llm",
    reason=False,
    confidence_score=False,
    retry_kwargs={},
    **kwargs,
):

    async def _inner():
        out_ = await _score(
            instruction=instruction,
            context=context,
            score_range=score_range,
            inclusive=inclusive,
            num_digit=num_digit,
            reason=reason,
            default_key=default_key,
            confidence_score=confidence_score,
            method=method,
            **kwargs,
        )
        if out_ is None:
            raise ValueError("No output from the model")

        return out_

    if "retries" not in retry_kwargs:
        retry_kwargs["retries"] = 2

    if "delay" not in retry_kwargs:
        retry_kwargs["delay"] = 0.5

    return await func_call.rcall(_inner, **retry_kwargs)


def _create_score_config(
    instruction,
    score_range=(1, 10),
    inclusive=True,
    num_digit=0,
    reason=False,
    default_key="score",
    confidence_score=False,
    **kwargs,
):
    instruct = {
        "task": "score context according to the following constraints",
        "instruction": convert.to_str(instruction),
        "score_range": convert.to_str(score_range),
        "include_endpoints": "yes" if inclusive else "no",
    }

    return_precision = ""
    if num_digit == 0:
        return_precision = "integer"
    else:
        return_precision = f"num:{convert.to_str(num_digit)}f"

    extra_fields = kwargs.pop("output_fields", {})
    output_fields = {default_key: f"""a numeric score as {return_precision}"""}
    output_fields = {**output_fields, **extra_fields}

    if reason:
        output_fields["reason"] = "brief reason for the score"

    if confidence_score:
        output_fields["confidence_score"] = (
            "a numeric score between 0 to 1 formatted in num:0.2f"
        )

    if "temperature" not in kwargs:
        kwargs["temperature"] = 0.1

    return instruct, output_fields, kwargs


async def _score(
    context,
    instruction=None,
    score_range=(1, 10),
    inclusive=True,
    num_digit=0,
    default_key="score",
    method="llm",
    reason=False,
    confidence_score=False,
    **kwargs,
):
    _instruct, _output_fields, _kwargs = _create_score_config(
        instruction=instruction,
        score_range=score_range,
        inclusive=inclusive,
        num_digit=num_digit,
        reason=reason,
        default_key=default_key,
        confidence_score=confidence_score,
        **kwargs,
    )

    branch = Branch()
    out_ = ""

    if method == "llm":
        out_ = await branch.chat(
            _instruct,
            tools=None,
            context=context,
            output_fields=_output_fields,
            **_kwargs,
        )

    to_num_kwargs = {
        "upper_bound": score_range[1],
        "lower_bound": score_range[0],
        "num_type": int if num_digit == 0 else float,
        "precision": num_digit if num_digit != 0 else None,
    }

    return _handle_single_out(
        out_, default_key, to_type="num", to_type_kwargs=to_num_kwargs
    )
