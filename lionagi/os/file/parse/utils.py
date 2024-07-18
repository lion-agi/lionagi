from lion_core import CoreLib
from collections.abc import Callable
from typing import Any, Literal, TypedDict, Sequence


class KeysDict(TypedDict, total=False):
    """TypedDict for keys dictionary."""

    key: Any  # Represents any key-type pair


class ParseUtil:

    @staticmethod
    def fuzzy_parse_json(
        str_to_parse: str, suppress: bool = False
    ) -> dict[str, Any]:
        """
        Attempt to parse a JSON string, applying fixes for common issues.

        This function tries to parse the given JSON string using the `loads`
        function from the `json` module. If the initial parsing fails, it
        attempts to fix common formatting issues in the JSON string using the
        `fix_json_string` function and then tries parsing again. If the JSON
        string contains single quotes, they are replaced with double quotes
        before making a final attempt to parse the string.

        Args:
            str_to_parse: The JSON string to parse.

        Returns:
            The parsed JSON object as a dictionary.

        Raises:
            ValueError: If the JSON string cannot be parsed even after
                attempts to fix it.

        Example:
            >>> fuzzy_parse_json('{"key": "value"}')
            {'key': 'value'}
        """
        return CoreLib.fuzzy_parse_json(str_to_parse, surpress=suppress)

    @staticmethod
    def extract_json_block(
        str_to_parse: str,
        language: str = "json",
        regex_pattern: str | None = None,  # take priority over language parameter
        *,
        parser: Callable[[str], Any] = None,
    ) -> Any:
        """
        Extract and parse a JSON block from Markdown content.

        This function searches for a JSON block in the given Markdown string
        using a regular expression pattern. If a JSON block is found, it is
        parsed using the provided parser function.

        Args:
            str_to_parse: The Markdown content to search.
            regex_pattern: An optional regular expression pattern to use for
                finding the JSON block. If not provided, a default pattern
                that matches a JSON block enclosed in triple backticks is
                used.
            parser: A function to parse the extracted JSON string. If not
                provided, the `fuzzy_parse_json` function will be used.

        Returns:
            The result of parsing the JSON block with the provided parser
            function.

        Raises:
            ValueError: If no JSON block is found in the Markdown content.

        Example:
            >>> extract_json_block('```json\\n{"key": "value"}\\n```')
            {'key': 'value'}
        """
        return CoreLib.extract_json_block(
            str_to_parse=str_to_parse,
            language=language,
            regex_pattern=regex_pattern,
            parser=parser,
        )

    @staticmethod
    def extract_code_block(str_to_parse: str) -> str:
        """
        Extract code blocks from a given string containing Markdown code blocks.

        This function identifies code blocks enclosed by triple backticks (```)
        and extracts their content. It handles multiple code blocks and
        concatenates them with two newlines between each block.

        Args:
            code: The input string containing Markdown code blocks.

        Returns:
            Extracted code blocks concatenated with two newlines. If no code
            blocks are found, returns an empty string.

        Example:
            >>> text = "Some text\\n```python\\nprint('Hello')\\n```\\nMore text"
            >>> extract_code_blocks(text)
            "print('Hello')"
        """
        return CoreLib.extract_code_block(str_to_parse=str_to_parse)

    @staticmethod
    def md_to_json(
        str_to_parse: str,
        *,
        expected_keys: list[str] | None = None,
        parser: Callable[[str], Any] | None = None,
    ) -> dict[str, Any]:
        """
        Parse a JSON block from a Markdown string and validate its keys.

        This function extracts a JSON block from a Markdown string using the
        `extract_json_block` function and validates the presence of expected
        keys in the parsed JSON object.

        Args:
            str_to_parse: The Markdown string to parse.
            expected_keys: A list of keys expected to be present in the JSON
                object. If provided, the function will raise a ValueError if
                any of the expected keys are missing.
            parser: A custom parser function to parse the JSON string. If not
                provided, the `fuzzy_parse_json` function will be used.

        Returns:
            The parsed JSON object.

        Raises:
            ValueError: If the expected keys are not present in the JSON
                object or if no JSON block is found.
        """
        return CoreLib.md_to_json(
            str_to_parse=str_to_parse,
            expected_keys=expected_keys,
            parser=parser,
        )

    @staticmethod
    def extract_docstring_details(
        func: Callable, style: Literal["google", "rest"] = "google"
    ) -> tuple[str | None, dict[str, str]]:
        """
        Extract function description and parameter descriptions from docstring.

        Args:
            func: The function from which to extract docstring details.
            style: The style of docstring to parse ('google' or 'rest').

        Returns:
            A tuple containing the function description and a dictionary with
            parameter names as keys and their descriptions as values.

        Raises:
            ValueError: If an unsupported style is provided.

        Examples:
            >>> def example_function(param1: int, param2: str):
            ...     '''Example function.
            ...
            ...     Args:
            ...         param1 (int): The first parameter.
            ...         param2 (str): The second parameter.
            ...     '''
            ...     pass
            >>> description, params = extract_docstring_details(example_function)
            >>> description
            'Example function.'
            >>> params == {'param1': 'The first parameter.',
            ...            'param2': 'The second parameter.'}
            True
        """
        return CoreLib.extract_docstring_details(func, style)

    #new
    @staticmethod
    def validate_mapping(
        d_: dict[str, Any] | str,
        keys: Sequence[str] | KeysDict,
        /,
        *,
        score_func: Callable[[str, str], float] | None = None,
        fuzzy_match: bool = True,
        handle_unmatched: Literal["ignore", "raise", "remove", "fill", "force"] = "ignore",
        fill_value: Any = None,
        fill_mapping: dict[str, Any] | None = None,
        strict: bool = False,
    ) -> dict[str, Any]:
        """
        Force-validate a mapping against a set of expected keys.

        Takes an input `dict_` and attempts to convert it into a dictionary if
        it's a string. Then validates the dictionary against expected keys
        using the `force_validate_keys` function.

        Args:
            dict_: Input to be validated. Can be a dictionary or a string
                representing a dictionary.
            keys: List of expected keys or dictionary mapping keys to types.
            score_func: Function returning similarity score (0-1) for two
                strings. Defaults to None.
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
            The validated dictionary.

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
        return CoreLib.validate_mapping(
            d_,
            keys,
            score_func=score_func,
            fuzzy_match=fuzzy_match,
            handle_unmatched=handle_unmatched,
            fill_value=fill_value,
            fill_mapping=fill_mapping,
            strict=strict,
        )

    # new
    @staticmethod
    def function_to_schema(
        f_,  # renamed func to f_, made function and style positional-only
        style: Literal["google", "rest"] = "google",  # used Literal type
        /,
        *,  # made description and params_description keyword-only
        f_description=None,
        p_description=None,
    ) -> dict:
        """
        Generate a schema description for a given function.

        This function generates a schema description for the given function
        using typing hints and docstrings. The schema includes the function's
        name, description, and parameter details.

        Args:
            func (Callable): The function to generate a schema for.
            style (str): The docstring format. Can be 'google' (default) or
                'reST'.
            func_description (str, optional): A custom description for the
                function. If not provided, the description will be extracted
                from the function's docstring.
            params_description (dict, optional): A dictionary mapping
                parameter names to their descriptions. If not provided, the
                parameter descriptions will be extracted from the function's
                docstring.

        Returns:
            dict: A schema describing the function, including its name,
            description, and parameter details.

        Example:
            >>> def example_func(param1: int, param2: str) -> bool:
            ...     '''Example function.
            ...
            ...     Args:
            ...         param1 (int): The first parameter.
            ...         param2 (str): The second parameter.
            ...     '''
            ...     return True
            >>> schema = function_to_schema(example_func)
            >>> schema['function']['name']
            'example_func'
        """
        return CoreLib.function_to_schema(
            f_, style, f_description=f_description, p_description=p_description
        )

    # new
    @staticmethod
    def validate_keys(
        d_: dict[str, Any],
        keys: Sequence[str] | KeysDict,
        /,
        *,
        score_func: Callable[[str, str], float] | None = None,
        fuzzy_match: bool = True,
        handle_unmatched: Literal[
            "ignore", "raise", "remove", "fill", "force"
        ] = "ignore",
        fill_value: Any = None,
        fill_mapping: dict[str, Any] | None = None,
        strict: bool = False,
    ) -> dict[str, Any]:
        """
        Force-validate keys in a dictionary based on expected keys.

        Matches keys in the provided dictionary with expected keys, correcting
        mismatches using a similarity score function. Supports various modes
        for handling unmatched keys.

        Args:
            dict_: The dictionary to validate and correct keys for.
            keys: List of expected keys or dictionary mapping keys to types.
            score_func: Function returning similarity score (0-1) for two
                strings. Defaults to Jaro-Winkler similarity.
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
            ValueError: If handle_unmatched is "raise" and unmatched keys
                exist, or if strict is True and expected keys are missing.
        """
        return CoreLib.validate_keys(
            d_,
            keys,
            score_func=score_func,
            fuzzy_match=fuzzy_match,
            handle_unmatched=handle_unmatched,
            fill_value=fill_value,
            fill_mapping=fill_mapping,
            strict=strict,
        )

    @staticmethod
    def choose_most_similar(
        word: str,
        correct_words_list: Sequence[str],
        *,
        score_func: Callable[[str, str], float] | None = None,
    ) -> str | None:
        """
        Choose the most similar word from a list of correct words.

        This function compares the input word against a list of correct words
        using a similarity scoring function, and returns the most similar word.

        Args:
            word: The word to compare.
            correct_words_list: The list of correct words to compare against.
            score_func: A function to compute the similarity score between two
                words. Defaults to jaro_winkler_similarity.

        Returns:
            The word from correct_words_list that is most similar to the input
            word based on the highest similarity score, or None if the list is
            empty.
        """
        return CoreLib.choose_most_similar(
            word=word, correct_words_list=correct_words_list, score_func=score_func
        )
