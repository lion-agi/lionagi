import contextlib
from typing import Any, Callable, Union
from .md_to_json import fuzzy_parse_json, md_to_json
from .force_validate_keys import force_validate_keys


def force_validate_mapping(
    dict_: dict,
    keys: Union[dict, list[str]],
    score_func: Callable[[str, str], float] = None,
    fuzzy_match: bool = True,
    handle_unmatched: str = "ignore",
    fill_value: Any = None,
    fill_mapping: dict = None,
    strict: bool = False,
) -> dict:
    """
    Force-validate a mapping against a set of expected keys.

    This function takes an input `x` and attempts to convert it into a
    dictionary if it's a string. It then validates the dictionary against
    a set of expected keys using the `force_validate_keys` function.

    Args:
        x: The input to be validated. Can be a dictionary or a string
            representing a dictionary.
        keys: A list of expected keys or a dictionary mapping expected
            keys to their types.
        keys_only (bool): If True (default), only the keys specified in
            `keys` will be included in the output dictionary.
        all_keys (bool): If True (default), all keys specified in `keys`
            must be present in the input dictionary.

    Returns:
        dict: The validated dictionary.

    Raises:
        ValueError: If the input cannot be converted to a valid dictionary
            or if the validation fails.

    Example:
        >>> input_str = "{'name': 'John', 'age': 30}"
        >>> keys = ['name', 'age', 'city']
        >>> validated_dict = force_validate_mapping(input_str, keys)
        >>> validated_dict
        {'name': 'John', 'age': 30, 'city': None}
    """
    out_ = dict_

    if isinstance(out_, str):
        try:
            out_ = fuzzy_parse_json(out_)
        except Exception:
            try:
                out_ = md_to_json(out_)
            except Exception:
                with contextlib.suppress(Exception):
                    out_ = fuzzy_parse_json(out_.replace("'", '"'))

    if isinstance(out_, dict):
        try:
            return force_validate_keys(
                dict_=out_,
                keys=keys,
                score_func=score_func,
                handle_unmatched=handle_unmatched,
                fill_value=fill_value,
                fill_mapping=fill_mapping,
                strict=strict,
                fuzzy_match=fuzzy_match,
            )
        except Exception as e:
            raise ValueError(f"Failed to force_validate_dict for input: {dict_}") from e

    raise ValueError(f"Failed to force_validate_dict for input: {dict_}")
