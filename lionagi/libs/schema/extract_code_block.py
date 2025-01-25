# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import re


def extract_code_block(
    str_to_parse: str,
    return_as_list: bool = False,
    languages: list[str] | None = None,
    categorize: bool = False,
) -> str | list[str] | dict[str, list[str]]:
    """
    Extract code blocks from a given string containing
    Markdown-formatted text.

    This function identifies code blocks enclosed by triple
    backticks (```) or
    tildes (~~~), extracts their content, and can filter
    them based on specified
    programming languages. It provides options to return
    the extracted code
    blocks as a single concatenated string, a list, or a
    dictionary categorized
    by language.

    Args:
        str_to_parse: The input string containing Markdown
        code blocks.
        return_as_list: If True, returns a list of code
        blocks; otherwise, returns
            them as a single concatenated string separated
            by two newlines.
        languages: A list of languages to filter the code
        blocks. If None,
            extracts code blocks of all languages.
        categorize: If True, returns a dictionary mapping
        languages to lists of
            code blocks.

    Returns:
        Depending on the parameters:
            - A concatenated string of code blocks.
            - A list of code blocks.
            - A dictionary mapping languages to lists of
            code blocks.
    """
    code_blocks = []
    code_dict = {}

    pattern = re.compile(
        r"""
        ^(?P<fence>```|~~~)[ \t]*     # Opening fence ``` or ~~~
        (?P<lang>[\w+-]*)[ \t]*\n     # Optional language identifier
        (?P<code>.*?)(?<=\n)          # Code content
        ^(?P=fence)[ \t]*$            # Closing fence matching the opening
        """,
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )

    for match in pattern.finditer(str_to_parse):
        lang = match.group("lang") or "plain"
        code = match.group("code")

        if languages is None or lang in languages:
            if categorize:
                code_dict.setdefault(lang, []).append(code)
            else:
                code_blocks.append(code)

    if categorize:
        return code_dict
    elif return_as_list:
        return code_blocks
    else:
        return "\n\n".join(code_blocks)
