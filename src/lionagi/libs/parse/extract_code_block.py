# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import re

from lionagi.libs.base import CodeBlock


def extract_code_block(
    str_to_parse: str,
    languages: list[str] | None = None,
    categorize: bool = False,
) -> str | list[CodeBlock] | dict[str, list[CodeBlock]]:
    """
    Extracts code blocks from a Markdown-formatted string.

    Code blocks are identified by fences (``` or ~~~) and optionally
    annotated with a language. This function can return all blocks as
    a single string, a list of CodeBlock objects, or a dictionary keyed by language,
    each value being a list of CodeBlock objects.

    Args:
        str_to_parse (str): The input Markdown string.
        languages (list[str] | None): If provided, only return code blocks
            whose language matches one in this list. If None, return all.
        categorize (bool): If True, return a dictionary mapping each language
            to a list of CodeBlock objects.

    Returns:
        list[CodeBlock] | dict[str, list[CodeBlock]]:
            - If categorize=True: a dict mapping languages to lists of CodeBlock objects.
            - Otherwise: a list of CodeBlock objects.
    """
    code_blocks = []
    code_dict = {}

    pattern = re.compile(
        r"""
        ^[ \t]*(?P<fence>```|~~~)[ \t]*  # Opening fence with optional leading whitespace
        (?P<lang>[\w+-]*)[ \t]*\n        # Optional language
        (?P<code>.*?)                     # Code content
        (?:\n[ \t]*)?                     # Optional trailing newline
        ^[ \t]*(?P=fence)[ \t]*$         # Matching closing fence with optional leading whitespace
        """,
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )

    for match in pattern.finditer(str_to_parse):
        lang = match.group("lang") or "plain"
        code = match.group("code")
        # Ensure code ends with exactly one newline
        code = (code or "").rstrip("\n") + "\n"

        if languages is None or lang in languages:
            block = CodeBlock(lang=lang, code=code)
            if categorize:
                code_dict.setdefault(lang, []).append(block)
            else:
                code_blocks.append(block)

    if categorize:
        return code_dict
    return code_blocks
