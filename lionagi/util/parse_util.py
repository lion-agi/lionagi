import re

from typing import Any, Callable, List
from lionagi.util.convert_util import to_dict


md_json_char_map = {
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
    '"': '\\"'
}

class ParseUtil:

    @staticmethod
    def fuzzy_parse_json(str_to_parse: str, *, strict: bool = False):
        """
        Parses a potentially incomplete or malformed JSON string by adding missing closing brackets or braces.

        Tries to parse the input string as JSON and, on failure due to formatting errors, attempts to correct
        the string by appending necessary closing characters before retrying.

        Args:
            s (str): The JSON string to parse.
            strict (bool, optional): If True, enforces strict JSON syntax. Defaults to False.

        Returns:
            The parsed JSON object, typically a dictionary or list.

        Raises:
            ValueError: If parsing fails even after attempting to correct the string.

        Example:
            >>> fuzzy_parse_json('{"name": "John", "age": 30, "city": "New York"')
            {'name': 'John', 'age': 30, 'city': 'New York'}
        """
        try:
            return to_dict(str_to_parse, strict=strict)
        except:
            fixed_s = ParseUtil.fix_json_string(str_to_parse)
            try:
                return to_dict(fixed_s, strict=strict)
            except Exception as e:
                raise ValueError(f"Failed to parse JSON even after fixing attempts: {e}")


    @staticmethod
    def fix_json_string(str_to_parse: str) -> str:
        
        brackets = {'{': '}', '[': ']'}
        open_brackets = []
        
        for char in str_to_parse:
            if char in brackets:
                open_brackets.append(brackets[char])
            elif char in brackets.values():
                if not open_brackets or open_brackets[-1] != char:
                    raise ValueError("Mismatched or extra closing bracket found.")
                open_brackets.pop()

        return str_to_parse + ''.join(reversed(open_brackets))


    @staticmethod
    def escape_chars_in_json(value: str, char_map=None) -> str:
        
        def replacement(match):
            char = match.group(0)
            char_map = char_map or md_json_char_map
            return char_map.get(char, char)  # Default to the char itself if not in map

        # Match any of the special characters to be escaped.
        return re.sub(r'[\n\r\t"]', replacement, value)


    # inspired by langchain_core.output_parsers.json (MIT License)
    # https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/output_parsers/json.py
    @staticmethod
    def extract_code_block(
        str_to_parse: str, 
        language: str | None = None,
        regex_pattern: str | None = None,
        *, 
        parser: Callable[[str], Any]
    ) -> Any:
        
        if language:
            regex_pattern = rf"```{language}\n?(.*?)\n?```"
        else:
            regex_pattern = r"```\n?(.*?)\n?```"
        
        match = re.search(regex_pattern, str_to_parse, re.DOTALL)
        code_str = ''
        if match:
            code_str = match.group(1).strip()
        else:
            raise ValueError(f"No {language or 'specified'} code block found in the Markdown content.")
        
        return parser(code_str)

    @staticmethod
    def md_to_json(
        str_to_parse: str, *, 
        expected_keys: List[str] | None = None, 
        parser: Callable[[str], Any] | None = None,
    ) -> Any:
        
        json_obj = ParseUtil.extract_code_block(
            str_to_parse, language='json', parser=parser or ParseUtil.fuzzy_parse_json
        )

        if expected_keys:
            missing_keys = [key for key in expected_keys if key not in json_obj]
            if missing_keys:
                raise ValueError(f"Missing expected keys in JSON object: {', '.join(missing_keys)}")

        return json_obj



class StringMatch:

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
        s_len = len(s)
        t_len = len(t)
        if s_len == 0 and t_len == 0:
            return 1.0

        match_distance = (max(s_len, t_len) // 2) - 1
        s_matches = [False] * s_len
        t_matches = [False] * t_len

        matches = 0
        transpositions = 0

        for i in range(s_len):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, t_len)

            for j in range(start, end):
                if t_matches[j]:
                    continue
                if s[i] != t[j]:
                    continue
                s_matches[i] = t_matches[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(s_len):
            if not s_matches[i]:
                continue
            while not t_matches[k]:
                k += 1
            if s[i] != t[k]:
                transpositions += 1
            k += 1

        transpositions //= 2
        return (matches / s_len + matches / t_len + (matches - transpositions) / matches) / 3.0

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
        jaro_sim = StringMatch.jaro_distance(s, t)
        prefix_len = 0
        for s_char, t_char in zip(s, t):
            if s_char == t_char:
                prefix_len += 1
            else:
                break
            if prefix_len == 4:
                break
        return jaro_sim + (prefix_len * scaling * (1 - jaro_sim))

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
        m, n = len(a), len(b)
        # Initialize 2D array (m+1) x (n+1)
        d = [[0] * (n + 1) for _ in range(m + 1)]

        # Populate the base case values
        for i in range(m + 1):
            d[i][0] = i
        for j in range(n + 1):
            d[0][j] = j

        # Compute the distance
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if a[i - 1] == b[j - 1]:
                    cost = 0
                else:
                    cost = 1
                d[i][j] = min(d[i - 1][j] + 1,  # deletion
                              d[i][j - 1] + 1,  # insertion
                              d[i - 1][j - 1] + cost)  # substitution
        return d[m][n]
