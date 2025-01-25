# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any

from lionagi.utils import to_dict


def in_notebook() -> bool:
    """
    Checks if we're running inside a Jupyter notebook.
    Returns True if yes, False otherwise.
    """
    try:
        from IPython import get_ipython

        shell = get_ipython().__class__.__name__
        return "ZMQInteractiveShell" in shell
    except Exception:
        return False


def format_dict(data: Any, indent: int = 0) -> str:
    """
    Recursively format Python data (dicts, lists, strings, etc.) into a
    YAML-like readable string.

    - Multi-line strings are displayed using a '|' block style, each line indented.
    - Lists are shown with a '- ' prefix per item at the appropriate indentation.
    - Dict keys are shown as "key:" lines, with values on subsequent lines if complex.
    """
    lines = []
    prefix = "  " * indent  # 2 spaces per indent level

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                # Nested dict
                lines.append(f"{prefix}{key}:")
                lines.append(format_dict(value, indent + 1))
            elif isinstance(value, list):
                # List under a key
                lines.append(f"{prefix}{key}:")
                for item in value:
                    item_str = format_dict(item, indent + 2).lstrip()
                    lines.append(f"{prefix}  - {item_str}")
            elif isinstance(value, str) and "\n" in value:
                # Multi-line string
                lines.append(f"{prefix}{key}: |")
                subprefix = "  " * (indent + 1)
                for line in value.splitlines():
                    lines.append(f"{subprefix}{line}")
            else:
                # Simple single-line scalar
                item_str = format_dict(value, indent + 1).lstrip()
                lines.append(f"{prefix}{key}: {item_str}")
        return "\n".join(lines)

    elif isinstance(data, list):
        # For top-level or nested lists
        for item in data:
            item_str = format_dict(item, indent + 1).lstrip()
            lines.append(f"{prefix}- {item_str}")
        return "\n".join(lines)

    # Base case: single-line scalar
    return prefix + str(data)


def as_readable(
    input_: Any,
    /,
    *,
    md: bool = False,
    format_curly: bool = False,
    display_str: bool = False,
    max_chars: int | None = None,
) -> str:
    """
    Convert `input_` into a human-readable string. If `format_curly=True`, uses
    a YAML-like style (`format_dict`). Otherwise, pretty-printed JSON.

    - For Pydantic models or nested data, uses `to_dict` to get a dictionary.
    - If the result is a list of items, each is processed and concatenated.

    Args:
        input_: The data to convert (could be a single item or list).
        md: If True, wraps the final output in code fences for Markdown display.
        format_curly: If True, use `format_dict`. Otherwise, produce JSON text.

    Returns:
        A formatted string representation of `input_`.
    """

    # 1) Convert the input to a Python dict/list structure
    #    (handles recursion, Pydantic models, etc.)
    def to_dict_safe(obj: Any) -> Any:
        # Attempt to call to_dict with typical recursion flags
        to_dict_kwargs = {
            "use_model_dump": True,
            "fuzzy_parse": True,
            "recursive": True,
            "recursive_python_only": False,
            "max_recursive_depth": 5,
        }
        return to_dict(obj, **to_dict_kwargs)

    def _inner(i_: Any) -> Any:
        try:
            if isinstance(i_, list):
                # Already a list. Convert each item
                items = [to_dict_safe(x) for x in i_]
            else:
                # Single item
                maybe_list = to_dict_safe(i_)
                # If it's a list, store as items; else just single
                items = (
                    maybe_list
                    if isinstance(maybe_list, list)
                    else [maybe_list]
                )
        except Exception:
            # If conversion fails, fallback to str
            return str(i_)

        # 2) For each item in `items`, either format with YAML-like or JSON
        rendered = []
        for item in items:
            if format_curly:
                # YAML-like
                rendered.append(format_dict(item))
            else:
                # JSON approach
                try:
                    # Provide indentation, ensure ASCII not forced
                    rendered.append(
                        json.dumps(item, indent=2, ensure_ascii=False)
                    )
                except Exception:
                    # fallback
                    rendered.append(str(item))

        # 3) Combine
        final_str = "\n\n".join(rendered).strip()

        # 4) If Markdown requested, wrap with code fences
        #    - If we used format_curly, we might do "```yaml" instead. But user specifically asked for JSON code blocks previously
        if md:
            if format_curly:
                return f"```yaml\n{final_str}\n```"
            else:
                return f"```json\n{final_str}\n```"

        return final_str

    str_ = _inner(input_).strip()
    if max_chars is not None and len(str_) > max_chars:
        str1 = str_[:max_chars] + "...\n\n[Truncated output]\n\n"
        if str_.endswith("\n```"):
            str1 += "```"
        str_ = str1
    if display_str:
        if md and in_notebook():
            # If in IPython environment, display Markdown
            from IPython.display import Markdown, display

            display(Markdown(str_))
        else:
            # Otherwise, just print the string
            print(str_)
    else:
        return str_
