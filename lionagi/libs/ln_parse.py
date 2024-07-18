from lion_core import LN_UNDEFINED, CoreLib
from collections.abc import Callable
import re
from typing import Any, Literal, TypedDict, Sequence
import numpy as np
from typing_extensions import deprecated


class KeysDict(TypedDict, total=False):
    """TypedDict for keys dictionary."""

    key: Any  # Represents any key-type pair


class ParseUtil:

    # removed `strict` parameter in 0.2.3 as it was not used
    # reimplemented with lion_core.libs.parsers.fuzzy_parse_json
    # strict parameter already doesn't do anything, kept for backwards compatibility will be removed in 1.0.0
    # made str_tp_parse a positional-only parameter
    # made strict a keyword-only parameter
    @staticmethod
    def fuzzy_parse_json(
        str_to_parse: str, /, *, strict=LN_UNDEFINED
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
        return CoreLib.fuzzy_parse_json(str_to_parse)

    # moved implementation to lion_core.libs.parsers._fuzzy_parse_json
    # no change in implementation, will be deprecated in v1.0.0, with no replacement
    # use fuzzy_parse_json then json_dump instead
    @deprecated
    @staticmethod
    def fix_json_string(str_to_parse: str) -> str:
        """
        Fix a JSON string by ensuring all brackets are properly closed.

        This function iterates through the characters of the JSON string and
        keeps track of the opening brackets encountered. If a closing bracket
        is found without a matching opening bracket or if there are extra
        closing brackets, a ValueError is raised. Any remaining opening
        brackets at the end of the string are closed with their corresponding
        closing brackets.

        Args:
            str_to_parse: The JSON string to fix.

        Returns:
            The fixed JSON string with properly closed brackets.

        Raises:
            ValueError: If mismatched or extra closing brackets are found.

        Example:
            >>> fix_json_string('{"key": "value"')
            '{"key": "value"}'
        """
        return CoreLib.fix_json_string(str_to_parse)

    @deprecated  # internal methods, moved into lion_core, will remove in lionagi in 1.0.0
    @staticmethod  # with no replacement
    def escape_chars_in_json(value: str, char_map=None) -> str:
        """
        Escapes special characters in a JSON string using a specified character map.

        This method replaces newline, carriage return, tab, and double quote characters
        in a given string with their escaped versions defined in the character map. If no map is provided,
        a default mapping is used.

        Args:
                value: The string to be escaped.
                char_map: An optional dictionary mapping characters to their escaped versions.
                        If not provided, a default mapping that escapes newlines, carriage returns,
                        tabs, and double quotes is used.

        Returns:
                The escaped JSON string.

        Examples:
                >>> escape_chars_in_json('Line 1\nLine 2')
                'Line 1\\nLine 2'
        """
        return CoreLib.escape_chars_in_json(value, char_map)

    @staticmethod
    def extract_json_block(
        str_to_parse: str,
        language: str = "json",  # the language parameter will be removed in 1.0.0, use extract_code_block or custom regex_pattern
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

    # moved implementation to lion_core.libs.parsers._extract_code_blocks
    @deprecated  # use extract_code_block instead, will be removed in 1.0.0
    @staticmethod  # renamed to extract_code_block, and renamed the code parameter to str_to_parse
    def extract_code_blocks(code: str) -> str:
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
        return CoreLib.extract_code_block(code)

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

    @deprecated  # internal methods, moved into lion_core, will remove in lionagi in 1.0.0
    @staticmethod  # with no replacement, implementation moved to lion_core
    def _extract_docstring_details_google(
        func: Callable,
    ) -> tuple[str | None, dict[str, str]]:
        """
        Extract details from Google-style docstring.

        Args:
            func: The function from which to extract docstring details.

        Returns:
            A tuple containing the function description and a dictionary with
            parameter names as keys and their descriptions as values.

        Examples:
            >>> def example_function(param1: int, param2: str):
            ...     '''Example function.
            ...
            ...     Args:
            ...         param1 (int): The first parameter.
            ...         param2 (str): The second parameter.
            ...     '''
            ...     pass
            >>> description, params = _extract_docstring_details_google(
            ...     example_function)
            >>> description
            'Example function.'
            >>> params == {'param1': 'The first parameter.',
            ...            'param2': 'The second parameter.'}
            True
        """
        from lion_core.libs.parsers._extract_docstring import (
            _extract_docstring_details_google,
        )

        return _extract_docstring_details_google(func)

    @deprecated  # internal methods, moved into lion_core, will remove in lionagi in 1.0.0
    @staticmethod  # with no replacement, implementation moved to lion_core
    def _extract_docstring_details_rest(
        func: Callable,
    ) -> tuple[str | None, dict[str, str]]:
        """
        Extract details from reStructuredText-style docstring.

        Args:
            func: The function from which to extract docstring details.

        Returns:
            A tuple containing the function description and a dictionary with
            parameter names as keys and their descriptions as values.

        Examples:
            >>> def example_function(param1: int, param2: str):
            ...     '''Example function.
            ...
            ...     :param param1: The first parameter.
            ...     :type param1: int
            ...     :param param2: The second parameter.
            ...     :type param2: str
            ...     '''
            ...     pass
            >>> description, params = _extract_docstring_details_rest(
            ...     example_function)
            >>> description
            'Example function.'
            >>> params == {'param1': 'The first parameter.',
            ...            'param2': 'The second parameter.'}
            True
        """
        from lion_core.libs.parsers._extract_docstring import (
            _extract_docstring_details_rest,
        )

        return _extract_docstring_details_rest(func)

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

    @deprecated  # internal methods, moved into lion_core, will remove in lionagi in 1.0.0
    @staticmethod  # with no replacement
    def _python_to_json_type(py_type):
        """
        Converts a Python type to its JSON type equivalent.

        Args:
                py_type (str): The name of the Python type.

        Returns:
                str: The corresponding JSON type.

        Examples:
                >>> _python_to_json_type('str')
                'string'
                >>> _python_to_json_type('int')
                'number'
        """
        type_mapping = {
            "str": "string",
            "int": "number",
            "float": "number",
            "list": "array",
            "tuple": "array",
            "bool": "boolean",
            "dict": "object",
        }
        return type_mapping.get(py_type, "object")

    @deprecated  # moved into lion_core, will be removed in 1.0.0
    @staticmethod  # kept for backwards compatibility, use function_to_schema instead
    def _func_to_schema(
        func, style="google", func_description=None, params_description=None
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
            func=func,
            style=style,
            func_description=func_description,
            params_description=params_description,
        )

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

    @deprecated # use validate_keys instead, will be removed in 1.0.0
    @staticmethod
    def force_validate_keys(*args, **kwargs):
        return CoreLib.validate_keys(*args, **kwargs)

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


@deprecated  # will be removeed in 1.0.0,
class StringMatch:

    @deprecated  # internal method moved into lion_core, will be removed in lionagi in 1.0.0, with no replacement
    @staticmethod
    def jaro_distance(s, t):
        """
        Calculate the Jaro distance between two strings.

        The Jaro distance is a measure of similarity between two strings. The higher the Jaro distance,
        the more similar the two strings are. The score is normalized such that 0 equates to no similarity
        and 1 is an exact match.

        Args:
                s: The first string to compare.
                t: The second string to compare.

        Returns:
                A float representing the Jaro distance between the two strings, ranging from 0 to 1,
                where 1 means the strings are identical.

        Examples:
                >>> jaro_distance("martha", "marhta")
                0.9444444444444445
        """
        return CoreLib.jaro_distance(s, t)

    @deprecated  # internal method moved into lion_core, will be removed in lionagi in 1.0.0, with no replacement
    @staticmethod
    def jaro_winkler_similarity(s, t, scaling=0.1):
        """
        Calculate the Jaro-Winkler similarity between two strings.

        The Jaro-Winkler similarity is an extension of the Jaro similarity that gives more weight to strings
        that match from the beginning for a set prefix length. This method works well for short strings such as
        person names, and is designed to improve the scoring of strings that have a common prefix.

        Args:
                s: The first string to compare.
                t: The second string to compare.
                scaling: The scaling factor for how much the score is adjusted upwards for having common prefixes.
                                 The scaling factor should be less than 1, and a typical value is 0.1.

        Returns:
                A float representing the Jaro-Winkler similarity between the two strings, ranging from 0 to 1,
                where 1 means the strings are identical.

        Examples:
                >>> jaro_winkler_similarity("dixon", "dicksonx")
                0.8133333333333332
        """
        return CoreLib.jaro_winkler_similarity(s, t, scaling)

    @deprecated  # internal method moved into lion_core, will be removed in lionagi in 1.0.0, with no replacement
    @staticmethod
    def levenshtein_distance(a, b):
        """
        Calculate the Levenshtein distance between two strings.

        The Levenshtein distance is a string metric for measuring the difference between two sequences.
        It is calculated as the minimum number of single-character edits (insertions, deletions, or substitutions)
        required to change one word into the other. Each operation has an equal cost.

        Args:
                a: The first string to compare.
                b: The second string to compare.

        Returns:
                An integer representing the Levenshtein distance between the two strings.

        Examples:
                >>> levenshtein_distance("kitten", "sitting")
                3
        """
        return CoreLib.levenshtein_distance(a, b)

    @deprecated  # moved in ParseUtil, these paremter set are all deprecated, use the new method in ParseUtil.validate_keys
    @staticmethod
    def correct_dict_keys(keys: dict | list[str], dict_, score_func=None):
        if score_func is None:
            score_func = StringMatch.jaro_winkler_similarity

        fields_set = set(keys if isinstance(keys, list) else keys.keys())
        corrected_out = {}
        used_keys = set()

        for k, v in dict_.items():
            if k in fields_set:
                corrected_out[k] = v
                fields_set.remove(k)  # Remove the matched key
                used_keys.add(k)
            else:
                # Calculate Jaro-Winkler similarity scores for each potential match
                scores = np.array([score_func(k, field) for field in fields_set])
                # Find the index of the highest score
                max_score_index = np.argmax(scores)
                # Select the best match based on the highest score
                best_match = list(fields_set)[max_score_index]

                corrected_out[best_match] = v
                fields_set.remove(best_match)  # Remove the matched key
                used_keys.add(best_match)

        if len(used_keys) < len(dict_):
            for k, v in dict_.items():
                if k not in used_keys:
                    corrected_out[k] = v

        return corrected_out

    @deprecated  # moved in ParseUtil
    @staticmethod
    def choose_most_similar(word, correct_words_list, score_func=None):

        if score_func is None:
            score_func = StringMatch.jaro_winkler_similarity

        # Calculate Jaro-Winkler similarity scores for each potential match
        scores = np.array(
            [
                score_func(str(word), str(correct_word))
                for correct_word in correct_words_list
            ]
        )
        # Find the index of the highest score
        max_score_index = np.argmax(scores)
        return correct_words_list[max_score_index]

    @deprecated  # moved in ParseUtil, renamed to validate_mapping
    @staticmethod
    def force_validate_dict(x, keys: dict | list[str]) -> dict:
        out_ = x

        if isinstance(out_, str):
            # first try to parse it straight as a fuzzy json

            try:
                out_ = ParseUtil.fuzzy_parse_json(out_)
                return StringMatch.correct_dict_keys(keys, out_)

            except:
                try:
                    out_ = ParseUtil.md_to_json(out_)
                    return StringMatch.correct_dict_keys(keys, out_)

                except Exception:
                    try:
                        # if failed we try to extract the json block and parse it
                        out_ = ParseUtil.md_to_json(out_)
                        return StringMatch.correct_dict_keys(keys, out_)

                    except Exception:
                        # if still failed we try to extract the json block using re and parse it again
                        match = re.search(r"```json\n({.*?})\n```", out_, re.DOTALL)
                        if match:
                            out_ = match.group(1)
                            try:
                                out_ = ParseUtil.fuzzy_parse_json(out_)
                                return StringMatch.correct_dict_keys(keys, out_)

                            except:
                                try:
                                    out_ = ParseUtil.fuzzy_parse_json(
                                        out_.replace("'", '"')
                                    )
                                    return StringMatch.correct_dict_keys(keys, out_)
                                except:
                                    pass

        if isinstance(out_, dict):
            try:
                return StringMatch.correct_dict_keys(keys, out_)
            except Exception as e:
                raise ValueError(f"Failed to force_validate_dict for input: {x}") from e
