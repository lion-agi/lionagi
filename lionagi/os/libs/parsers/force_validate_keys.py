from typing import Any, Union, Callable
import numpy as np
from lionagi.os.libs.algorithms.jaro_distance import jaro_winkler_similarity


def force_validate_keys(
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
    Force-validate keys in a dictionary based on a set of expected keys.

    This function matches the keys in the provided dictionary with the
    expected keys, correcting mismatched keys using a similarity score
    function. It supports various modes for handling unmatched keys.

    Args:
        keys: A list of expected keys or a dictionary mapping expected
            keys to their types.
        dict_: The dictionary to validate and correct keys for.
        score_func: A function that takes two strings and returns a
            similarity score between 0 and 1. Defaults to Jaro-Winkler
            similarity.
        handle_unmatched: Specifies how to handle unmatched keys. Can be
            one of the following:
            - "ignore": Keep unmatched keys in the output dictionary.
            - "raise": Raise a ValueError if there are unmatched keys.
            - "remove": Remove unmatched keys from the output dictionary.
            - "fill": Fill unmatched keys with a default value or mapping.
            - "force": Combine "fill" and "remove" behaviors.
        fill_value: A single default value to use for filling unmatched
            keys when handle_unmatched is set to "fill" or "force".
        fill_mapping: A dictionary mapping unmatched keys to their
            default values when handle_unmatched is set to "fill" or
            "force".
        strict: If True, raises a ValueError if any expected key is not
            found in the input dictionary.

    Returns:
        A new dictionary with validated and corrected keys.

    Raises:
        ValueError: If handle_unmatched is set to "raise" and there are
            unmatched keys, or if strict is True and any expected key is
            not found in the input dictionary.
    """
    fields_set = set(keys) if isinstance(keys, list) else set(keys.keys())

    if strict:
        if any(k not in dict_ for k in fields_set):
            raise ValueError(f"Failed to force_validate_keys for input: {dict_}")

    if set(dict_.keys()) == fields_set:
        return dict_

    if score_func is None:
        score_func = jaro_winkler_similarity

    corrected_out = {}
    used_keys = set()
    old_used_keys = set()

    # TODO: need fixing, this logic is wrong
    if fuzzy_match:
        for k, v in dict_.items():
            if k in fields_set:
                corrected_out[k] = v
                fields_set.remove(k)  # Remove the matched key
                used_keys.add(k)
                old_used_keys.add(k)
            else:
                # Calculate similarity scores for each potential match
                scores = np.array([score_func(k, field) for field in fields_set])
                if len(scores) == 0:
                    break
                # Find the index of the highest score
                max_score_index = np.argmax(scores)
                # Select the best match based on the highest score
                best_match = list(fields_set)[max_score_index]

                corrected_out[best_match] = v
                fields_set.remove(best_match)  # Remove the matched key
                used_keys.add(best_match)
                old_used_keys.add(k)

        for k, v in dict_.items():
            if k not in old_used_keys:
                corrected_out[k] = v

        if len(used_keys) == len(dict_) == fields_set:
            return corrected_out

    if handle_unmatched == "ignore":
        return corrected_out

    if handle_unmatched in ["force", "remove"]:
        for k in set(dict_.keys()) - used_keys:
            corrected_out.pop(k, None)
        if handle_unmatched == "remove":
            return corrected_out

    if handle_unmatched in ["force", "fill"]:
        for k in fields_set - used_keys:
            if fill_mapping:
                corrected_out[k] = fill_mapping.get(k, fill_value)
            else:
                corrected_out[k] = fill_value
        if handle_unmatched == "fill":
            return corrected_out

    if handle_unmatched == "force":
        return corrected_out

    raise ValueError(f"Failed to force_validate_keys for input: {dict_}")
