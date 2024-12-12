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
        return_as_list (bool): If True, return code blocks as a list of CodeBlock objects.
            Otherwise, return a single string separated by double newlines.
        languages (list[str] | None): If provided, only return code blocks
            whose language matches one in this list. If None, return all.
        categorize (bool): If True, return a dictionary mapping each language
            to a list of CodeBlock objects.

    Returns:
        str | list[CodeBlock] | dict[str, list[CodeBlock]]:
            - If categorize=True: a dict mapping languages to lists of CodeBlock objects.
            - Else if return_as_list=True: a list of CodeBlock objects.
            - Otherwise: a single string of all code blocks separated by two newlines.
    """
    code_blocks = []
    code_dict = {}

    pattern = re.compile(
        r"""
        ^(?P<fence>```|~~~)[ \t]*       # Opening fence
        (?P<lang>[\w+-]*)[ \t]*\n       # Optional language
        (?P<code>.*?)(?<=\n)            # Code content
        ^(?P=fence)[ \t]*$              # Matching closing fence
        """,
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )

    for match in pattern.finditer(str_to_parse):
        lang = match.group("lang") or "plain"
        code = match.group("code")

        if languages is None or lang in languages:
            block = CodeBlock(lang=lang, code=code)
            if categorize:
                code_dict.setdefault(lang, []).append(block)
            else:
                code_blocks.append(block)

    if categorize:
        return code_dict
    return code_blocks
