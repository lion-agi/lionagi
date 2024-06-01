def _has_action_keys(dict_):
    return list(dict_.keys()) >= ["function", "arguments"]


def _fix_action_field(x, discard_=True):
    corrected = []
    if isinstance(x, str):
        x = ParseUtil.fuzzy_parse_json(x)

    try:
        x = to_list(x)

        for i in x:
            i = to_dict(i)
            if _has_action_keys(i):
                corrected.append(i)
            elif not discard_:
                raise ValueError(f"Invalid action field: {i}")
    except Exception as e:
        raise ValueError(f"Invalid action field: {e}") from e

    return corrected


def check_action_field(x, fix_=True, **kwargs):
    if (
        isinstance(x, list)
        and is_same_dtype(x, dict)
        and all(_has_action_keys(y) for y in x)
    ):
        return x
    try:
        x = _fix_action_field(x, fix_)
        return x
    except Exception as e:
        raise ValueError("Invalid action field type.") from e
