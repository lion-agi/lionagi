import contextlib
from lionagi.libs import ParseUtil, StringMatch, convert, func_call


def _parse_out(out_):
    if isinstance(out_, str):
        try:
            out_ = ParseUtil.md_to_json(out_)
        except Exception:
            with contextlib.suppress(Exception):
                out_ = ParseUtil.fuzzy_parse_json(out_.strip("```json").strip("```"))
    return out_


def _handle_single_out(
    out_,
    default_key,
    choices=None,
    to_type="dict",
    to_type_kwargs=None,
    to_default=True,
):

    if to_type_kwargs is None:
        to_type_kwargs = {}
    out_ = _parse_out(out_)

    if default_key not in out_:
        raise ValueError(f"Key {default_key} not found in output")

    answer = out_[default_key]

    if (
        choices is not None
        and answer not in choices
        and convert.strip_lower(out_) in ["", "none", "null", "na", "n/a"]
    ):
        raise ValueError(f"Answer {answer} not in choices {choices}")

    if to_type == "str":
        out_[default_key] = convert.to_str(answer, **to_type_kwargs)

    elif to_type == "num":
        out_[default_key] = convert.to_num(answer, **to_type_kwargs)

    return out_[default_key] if to_default and len(out_.keys()) == 1 else out_


def _handle_multi_out(
    out_,
    default_key,
    choices=None,
    to_type="dict",
    to_type_kwargs=None,
    to_default=True,
    include_mapping=False,
):
    if to_type_kwargs is None:
        to_type_kwargs = {}
    if include_mapping:
        for i in out_:
            i[default_key] = _handle_single_out(
                i[default_key],
                choices=choices,
                default_key=default_key,
                to_type=to_type,
                to_type_kwargs=to_type_kwargs,
                to_default=to_default,
            )
    else:
        _out = []
        for i in out_:
            i = _handle_single_out(
                i,
                choices=choices,
                default_key=default_key,
                to_type=to_type,
                to_type_kwargs=to_type_kwargs,
                to_default=to_default,
            )
            _out.append(i)

    return out_ if len(out_) > 1 else out_[0]
