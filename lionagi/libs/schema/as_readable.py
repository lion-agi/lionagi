# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any

from lionagi.utils import to_dict


def as_readable_json(input_: Any, /, **kwargs) -> str:
    """Convert input to a human-readable JSON string.

    Args:
        input_: Object to convert to readable JSON
        **kwargs: Additional arguments passed to json.dumps()

    Returns:
        A formatted, human-readable JSON string

    Raises:
        ValueError: If conversion to JSON fails
    """
    # Extract to_dict kwargs
    to_dict_kwargs = {
        "use_model_dump": True,
        "fuzzy_parse": True,
        "recursive": True,
        "recursive_python_only": False,
        "max_recursive_depth": 5,
    }
    to_dict_kwargs.update(kwargs)

    # Handle empty input
    if not input_:
        if isinstance(input_, list):
            return ""
        return "{}"

    try:
        if isinstance(input_, list):
            # For lists, convert and format each item separately
            items = []
            for item in input_:
                dict_ = to_dict(item, **to_dict_kwargs)
                items.append(
                    json.dumps(
                        dict_,
                        indent=2,
                        ensure_ascii=False,
                        default=lambda o: to_dict(o),
                    )
                )
            return "\n\n".join(items)

        # Handle single items
        dict_ = to_dict(input_, **to_dict_kwargs)

        # Extract json.dumps kwargs from input kwargs
        json_kwargs = {
            "indent": 2,
            "ensure_ascii": kwargs.get("ensure_ascii", False),
            "default": lambda o: to_dict(o),
        }

        # Add any other JSON-specific kwargs
        for k in ["indent", "separators", "cls"]:
            if k in kwargs:
                json_kwargs[k] = kwargs[k]

        # Convert to JSON string
        if kwargs.get("ensure_ascii", False):
            # Force ASCII encoding for special characters
            return json.dumps(
                dict_,
                ensure_ascii=True,
                **{
                    k: v for k, v in json_kwargs.items() if k != "ensure_ascii"
                },
            )

        return json.dumps(dict_, **json_kwargs)

    except Exception as e:
        raise ValueError(
            f"Failed to convert input to readable JSON: {e}"
        ) from e


def as_readable(input_: Any, /, *, md: bool = False, **kwargs) -> str:
    """Convert input to readable string with optional markdown formatting.

    Args:
        input_: Object to convert
        md: Whether to wrap in markdown block
        **kwargs: Additional arguments for as_readable_json()

    Returns:
        Formatted string representation
    """
    try:
        result = as_readable_json(input_, **kwargs)
        if md:
            return f"```json\n{result}\n```"
        return result

    except Exception:
        if md:
            return f"```json\n{str(input_)}\n```"
        return str(input_)
