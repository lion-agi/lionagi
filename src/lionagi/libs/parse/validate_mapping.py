# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence
from typing import Any, Literal, TypedDict

from .string_similarity import string_similarity
from .to_dict import to_dict
from .to_json import to_json


class KeysDict(TypedDict):
    """Dictionary mapping keys to their expected types."""

    pass


def validate_keys(
    d_: dict[str, Any],
    keys: Sequence[str] | KeysDict,
    /,
    *,
    similarity_threshold: float = 0.85,
    fuzzy_match: bool = True,
    handle_unmatched: Literal[
        "ignore", "raise", "remove", "fill", "force"
    ] = "ignore",
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """
    Validate and correct dictionary keys based on expected keys using string similarity.

    Args:
        d_: The dictionary to validate and correct keys for.
        keys: List of expected keys or dictionary mapping keys to types.
        similarity_algo: String similarity algorithm to use or custom function.
        similarity_threshold: Minimum similarity score for fuzzy matching.
        fuzzy_match: If True, use fuzzy matching for key correction.
        handle_unmatched: Specifies how to handle unmatched keys:
            - "ignore": Keep unmatched keys in output.
            - "raise": Raise ValueError if unmatched keys exist.
            - "remove": Remove unmatched keys from output.
            - "fill": Fill unmatched keys with default value/mapping.
            - "force": Combine "fill" and "remove" behaviors.
        fill_value: Default value for filling unmatched keys.
        fill_mapping: Dictionary mapping unmatched keys to default values.
        strict: If True, raise ValueError if any expected key is missing.

    Returns:
        A new dictionary with validated and corrected keys.

    Raises:
        ValueError: If validation fails based on specified parameters.
        TypeError: If input types are invalid.
        AttributeError: If key validation fails.
    """
    # Input validation
    if not isinstance(d_, dict):
        raise TypeError("First argument must be a dictionary")
    if keys is None:
        raise TypeError("Keys argument cannot be None")
    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError("similarity_threshold must be between 0.0 and 1.0")

    # Extract expected keys
    fields_set = set(keys) if isinstance(keys, list) else set(keys.keys())
    if not fields_set:
        return d_.copy()  # Return copy of original if no expected keys

    # Initialize output dictionary and tracking sets
    corrected_out = {}
    matched_expected = set()
    matched_input = set()

    # First pass: exact matches
    for key in d_:
        if key in fields_set:
            corrected_out[key] = d_[key]
            matched_expected.add(key)
            matched_input.add(key)

    # Second pass: fuzzy matching if enabled
    if fuzzy_match:
        remaining_input = set(d_.keys()) - matched_input
        remaining_expected = fields_set - matched_expected

        for key in remaining_input:
            if not remaining_expected:
                break

            matches = string_similarity(
                key,
                list(remaining_expected),
                threshold=similarity_threshold,
                return_most_similar=True,
                case_sensitive=True,
            )

            if matches:
                match = matches
                corrected_out[match] = d_[key]
                matched_expected.add(match)
                matched_input.add(key)
                remaining_expected.remove(match)
            elif handle_unmatched == "ignore":
                corrected_out[key] = d_[key]

    # Handle unmatched keys based on handle_unmatched parameter
    unmatched_input = set(d_.keys()) - matched_input
    unmatched_expected = fields_set - matched_expected

    if handle_unmatched == "raise" and unmatched_input:
        raise ValueError(f"Unmatched keys found: {unmatched_input}")

    elif handle_unmatched == "ignore":
        for key in unmatched_input:
            corrected_out[key] = d_[key]

    elif handle_unmatched in ("fill", "force"):
        # Fill missing expected keys
        for key in unmatched_expected:
            if fill_mapping and key in fill_mapping:
                corrected_out[key] = fill_mapping[key]
            else:
                corrected_out[key] = fill_value

        # For "fill" mode, also keep unmatched original keys
        if handle_unmatched == "fill":
            for key in unmatched_input:
                corrected_out[key] = d_[key]

    # Check strict mode
    if strict and unmatched_expected:
        raise ValueError(f"Missing required keys: {unmatched_expected}")

    return corrected_out


def validate_mapping(
    d: Any,
    keys: Sequence[str] | KeysDict,
    /,
    *,
    similarity_threshold: float = 0.85,
    fuzzy_match: bool = True,
    handle_unmatched: Literal[
        "ignore", "raise", "remove", "fill", "force"
    ] = "ignore",
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    strict: bool = False,
    suppress_conversion_errors: bool = False,
) -> dict[str, Any]:
    """
    Validate and correct any input into a dictionary with expected keys.

    Args:
        d: Input to validate. Can be:
            - Dictionary
            - JSON string or markdown code block
            - XML string
            - Object with to_dict/model_dump method
            - Any type convertible to dictionary
        keys: List of expected keys or dictionary mapping keys to types.
        similarity_algo: String similarity algorithm or custom function.
        similarity_threshold: Minimum similarity score for fuzzy matching.
        fuzzy_match: If True, use fuzzy matching for key correction.
        handle_unmatched: How to handle unmatched keys:
            - "ignore": Keep unmatched keys
            - "raise": Raise error for unmatched keys
            - "remove": Remove unmatched keys
            - "fill": Fill missing keys with default values
            - "force": Combine "fill" and "remove" behaviors
        fill_value: Default value for filling unmatched keys.
        fill_mapping: Dictionary mapping keys to default values.
        strict: Raise error if any expected key is missing.
        suppress_conversion_errors: Return empty dict on conversion errors.

    Returns:
        Validated and corrected dictionary.

    Raises:
        ValueError: If input cannot be converted or validation fails.
        TypeError: If input types are invalid.
    """
    if d is None:
        raise TypeError("Input cannot be None")

    # Try converting to dictionary
    try:
        if isinstance(d, str):
            # First try to_json for JSON strings and code blocks
            try:
                json_result = to_json(d)
                dict_input = (
                    json_result[0]
                    if isinstance(json_result, list)
                    else json_result
                )
            except Exception:
                # Fall back to to_dict for other string formats
                dict_input = to_dict(
                    d, str_type="json", fuzzy_parse=True, suppress=True
                )
        else:
            dict_input = to_dict(
                d, use_model_dump=True, fuzzy_parse=True, suppress=True
            )

        if not isinstance(dict_input, dict):
            if suppress_conversion_errors:
                dict_input = {}
            else:
                raise ValueError(
                    f"Failed to convert input to dictionary: {type(dict_input)}"
                )

    except Exception as e:
        if suppress_conversion_errors:
            dict_input = {}
        else:
            raise ValueError(f"Failed to convert input to dictionary: {e}")

    # Validate the dictionary
    return validate_keys(
        dict_input,
        keys,
        similarity_threshold=similarity_threshold,
        fuzzy_match=fuzzy_match,
        handle_unmatched=handle_unmatched,
        fill_value=fill_value,
        fill_mapping=fill_mapping,
        strict=strict,
    )
