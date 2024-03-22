from lionagi.libs import func_call
from ..branch import Branch
from ..session import Session
from .utils import _handle_single_out, _handle_multi_out


async def predict(
    sentence,
    *,
    num_sentences=1,
    default_key="answer",
    confidence_score=False,
    reason=False,
    retry_kwargs=None,
    include_mapping=False,
    **kwargs,
):
    if retry_kwargs is None:
        retry_kwargs = {}
    return await _force_predict(
        sentence=sentence,
        num_sentences=num_sentences,
        default_key=default_key,
        confidence_score=confidence_score,
        reason=reason,
        retry_kwargs=retry_kwargs,
        include_mapping=include_mapping,
        **kwargs,
    )


async def _force_predict(
    sentence,
    num_sentences,
    default_key="answer",
    confidence_score=False,
    reason=False,
    retry_kwargs={},
    include_mapping=False,
    **kwargs,
):

    async def _inner1():
        out_ = await _predict(
            sentence=sentence,
            num_sentences=num_sentences,
            default_key=default_key,
            confidence_score=confidence_score,
            reason=reason,
            **kwargs,
        )
        if out_ is None:
            raise ValueError("No output from the model")

        return out_

    async def _inner2():
        out_ = await _parallel_predict(
            sentence=sentence,
            num_sentences=num_sentences,
            default_key=default_key,
            confidence_score=confidence_score,
            reason=reason,
            include_mapping=include_mapping,
            **kwargs,
        )

        if out_ is None:
            raise ValueError("No output from the model")

        return out_

    if "retries" not in retry_kwargs:
        retry_kwargs["retries"] = 2

    if "delay" not in retry_kwargs:
        retry_kwargs["delay"] = 0.5

    if (isinstance(sentence, (list, tuple)) and len(sentence) > 1) or include_mapping:
        return await func_call.rcall(_inner2, **retry_kwargs)

    return await func_call.rcall(_inner1, **retry_kwargs)


def _create_predict_config(
    num_sentences,
    default_key="answer",
    confidence_score=False,
    reason=False,
    **kwargs,
):
    instruct = {
        "task": f"predict the next {num_sentences} sentence(s)",
    }
    extra_fields = kwargs.pop("output_fields", {})

    output_fields = {default_key: "the predicted sentence(s)"}
    output_fields = {**output_fields, **extra_fields}

    if reason:
        output_fields["reason"] = "brief reason for the prediction"

    if confidence_score:
        output_fields["confidence_score"] = (
            "a numeric score between 0 to 1 formatted in num:0.2f"
        )

    if "temperature" not in kwargs:
        kwargs["temperature"] = 0.1

    return instruct, output_fields, kwargs


async def _predict(
    sentence,
    num_sentences,
    default_key="answer",
    confidence_score=False,
    reason=False,
    **kwargs,
):
    _instruct, _output_fields, _kwargs = _create_predict_config(
        num_sentences=num_sentences,
        default_key=default_key,
        confidence_score=confidence_score,
        reason=reason,
        **kwargs,
    )

    branch = Branch()

    out_ = await branch.chat(
        _instruct, context=sentence, output_fields=_output_fields, **_kwargs
    )

    return _handle_single_out(
        out_, default_key=default_key, to_type="str", to_default=True
    )


async def _parallel_predict(
    sentence,
    num_sentences,
    default_key="answer",
    confidence_score=False,
    reason=False,
    include_mapping=False,
    **kwargs,
):
    _instruct, _output_fields, _kwargs = _create_predict_config(
        num_sentences=num_sentences,
        default_key=default_key,
        confidence_score=confidence_score,
        reason=reason,
        **kwargs,
    )

    session = Session()

    out_ = await session.parallel_chat(
        _instruct,
        context=sentence,
        output_fields=_output_fields,
        include_mapping=include_mapping,
        **_kwargs,
    )

    return _handle_multi_out(
        out_,
        default_key=default_key,
        to_type="str",
        to_default=True,
        include_mapping=include_mapping,
    )
