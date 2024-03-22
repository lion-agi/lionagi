from lionagi.libs import StringMatch, func_call
from ..branch.branch import Branch
from .utils import _handle_single_out


async def select(
    context,
    choices,
    *,
    num_choices=1,
    method="llm",
    objective=None,
    default_key="answer",
    reason=False,
    confidence_score=False,
    retry_kwargs=None,
    **kwargs,
):
    if retry_kwargs is None:
        retry_kwargs = {}
    return await _force_select(
        context=context,
        choices=choices,
        num_choices=num_choices,
        method=method,
        objective=objective,
        default_key=default_key,
        reason=reason,
        confidence_score=confidence_score,
        retry_kwargs=retry_kwargs,
        **kwargs,
    )


async def _force_select(
    context,
    choices,
    num_choices=1,
    method="llm",
    objective=None,
    default_key="answer",
    reason=False,
    confidence_score=False,
    retry_kwargs={},
    **kwargs,
):

    async def _inner():
        out_ = await _select(
            context=context,
            choices=choices,
            num_choices=num_choices,
            method=method,
            objective=objective,
            default_key=default_key,
            reason=reason,
            confidence_score=confidence_score,
            retry_kwargs=retry_kwargs,
            **kwargs,
        )
        if out_ is None:
            raise ValueError("No output from the model")

        if isinstance(out_, dict) and out_[default_key] not in choices:
            v = StringMatch.choose_most_similar(out_.pop(default_key, ""), choices)
            out_[default_key] = v

        return out_

    if "retries" not in retry_kwargs:
        retry_kwargs["retries"] = 2

    if "delay" not in retry_kwargs:
        retry_kwargs["delay"] = 0.5

    return await func_call.rcall(_inner, **retry_kwargs)


def _create_select_config(
    choices,
    num_choices=1,
    objective=None,
    default_key="answer",
    reason=False,
    confidence_score=False,
    **kwargs,
):

    instruct = {"task": f"select {num_choices} from provided", "choices": choices}
    if objective is not None:
        instruct["objective"] = objective

    extra_fields = kwargs.pop("output_fields", {})
    output_fields = {default_key: "..."}
    output_fields = {**output_fields, **extra_fields}

    if reason:
        output_fields["reason"] = "brief reason for the selection"

    if confidence_score:
        output_fields["confidence_score"] = (
            "a numeric score between 0 to 1 formatted in num:0.2f"
        )

    if "temperature" not in kwargs:
        kwargs["temperature"] = 0.1

    return instruct, output_fields, kwargs


async def _select(
    context,
    choices,
    num_choices=1,
    method="llm",
    objective=None,
    default_key="answer",
    reason=False,
    confidence_score=False,
    **kwargs,
):

    _instruct, _output_fields, _kwargs = _create_select_config(
        choices=choices,
        num_choices=num_choices,
        objective=objective,
        default_key=default_key,
        reason=reason,
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

    return _handle_single_out(out_, default_key)
