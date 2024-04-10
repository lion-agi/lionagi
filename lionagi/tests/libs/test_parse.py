import unittest
from unittest.mock import patch

from lionagi.libs.ln_parse import *


class TestFuzzyParseJson(unittest.TestCase):

    def test_basic_json_parsing(self):
        """Test parsing of correctly formatted JSON strings."""
        json_str = '{"name": "John", "age": 30}'
        expected = {"name": "John", "age": 30}
        self.assertEqual(ParseUtil.fuzzy_parse_json(json_str), expected)

    def test_missing_closing_brackets(self):
        """Test JSON strings missing various closing brackets."""
        test_cases = [
            ('{"name": "John", "age": 30', {"name": "John", "age": 30}),
            ('[{"name": "John", "age": 30}', [{"name": "John", "age": 30}]),
            ('{"people": [{"name": "John"', {"people": [{"name": "John"}]}),
        ]
        for json_str, expected in test_cases:
            with self.subTest(json_str=json_str):
                self.assertEqual(ParseUtil.fuzzy_parse_json(json_str), expected)

    def test_nested_structures(self):
        """Test with nested JSON objects and arrays."""
        json_str = '{"data": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"'
        expected = {"data": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]}
        self.assertEqual(ParseUtil.fuzzy_parse_json(json_str), expected)

    def test_strict_mode(self):
        """Test the function's behavior in strict mode."""
        correct_json_str = '{"name": "John", "age": 30}'
        malformed_json_str = '{"name": "John", "age": 30'
        # Should work fine with correct JSON
        self.assertEqual(
            ParseUtil.fuzzy_parse_json(correct_json_str, strict=True),
            {"name": "John", "age": 30},
        )

    def test_error_handling(self):
        """Test with irreparably malformed JSON."""
        json_str = '{"name": "John", "age": 30 something wrong}'
        with self.assertRaises(ValueError):
            ParseUtil.fuzzy_parse_json(json_str)

    def test_escape_chars_in_json(self):
        """Test escaping special characters in JSON strings."""
        self.assertEqual(
            ParseUtil.escape_chars_in_json("Line 1\nLine 2"), "Line 1\\nLine 2"
        )
        self.assertEqual(ParseUtil.escape_chars_in_json('Quote: "'), 'Quote: \\"')

    def test_extract_code_block(self):
        """Test extracting and parsing code blocks from Markdown."""
        markdown = '```python\nprint("Hello, world!")\n```'
        result = ParseUtil.extract_code_block(
            markdown, language="python", parser=lambda x: x
        )
        self.assertEqual(result, 'print("Hello, world!")')

    def test_md_to_json(self):
        """Test extracting and validating JSON from Markdown content."""
        markdown = '```json\n{"key": "value"}\n```'
        result = ParseUtil.md_to_json(markdown, expected_keys=["key"])
        self.assertEqual(result, {"key": "value"})
        with self.assertRaises(ValueError):
            ParseUtil.md_to_json(markdown, expected_keys=["missing_key"])

    def test_jaro_distance(self):
        """Test Jaro distance calculations."""
        self.assertAlmostEqual(
            StringMatch.jaro_distance("martha", "marhta"), 0.9444444444444445, places=7
        )
        self.assertAlmostEqual(StringMatch.jaro_distance("", ""), 1.0)
        self.assertAlmostEqual(StringMatch.jaro_distance("abc", "abc"), 1.0)
        self.assertAlmostEqual(StringMatch.jaro_distance("abc", "def"), 0.0)

    def test_jaro_winkler_similarity(self):
        """Test Jaro-Winkler similarity calculations."""
        self.assertAlmostEqual(
            StringMatch.jaro_winkler_similarity("dixon", "dicksonx", scaling=0.1),
            0.8133333333333332,
            places=7,
        )
        self.assertAlmostEqual(
            StringMatch.jaro_winkler_similarity("martha", "marhta", scaling=0.1),
            0.9611111111111111,
            places=7,
        )
        self.assertAlmostEqual(
            StringMatch.jaro_winkler_similarity("", "", scaling=0.1), 1.0
        )
        self.assertAlmostEqual(
            StringMatch.jaro_winkler_similarity("abc", "abc", scaling=0.1), 1.0
        )
        self.assertAlmostEqual(
            StringMatch.jaro_winkler_similarity("abc", "def", scaling=0.1), 0.0
        )

    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculations."""
        self.assertEqual(StringMatch.levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(StringMatch.levenshtein_distance("", ""), 0)
        self.assertEqual(StringMatch.levenshtein_distance("book", "back"), 2)
        self.assertEqual(StringMatch.levenshtein_distance("book", ""), 4)
        self.assertEqual(StringMatch.levenshtein_distance("", "back"), 4)

    def test_extract_google_style(self):
        def sample_func():
            """
            Sample function.

            Args:
                    param1 (int): Description of param1.
                    param2 (str): Description of param2.
            """
            pass

        description, params = ParseUtil._extract_docstring_details_google(sample_func)
        self.assertEqual(description, "Sample function.")
        self.assertDictEqual(
            params,
            {"param1": "Description of param1.", "param2": "Description of param2."},
        )

    def test_extract_reST_style(self):
        def sample_func():
            """
            Sample function.

            :param param1: Description of param1.
            :type param1: int
            :param param2: Description of param2.
            :type param2: str
            """
            pass

        description, params = ParseUtil._extract_docstring_details_rest(sample_func)
        self.assertEqual(description, "Sample function.")
        self.assertDictEqual(
            params,
            {"param1": "Description of param1.", "param2": "Description of param2."},
        )

    @patch("lionagi.libs.ln_parse.ParseUtil._extract_docstring_details")
    def test_func_to_schema(self, mock_extract):
        mock_extract.return_value = (
            "Function description",
            {"param1": "Description of param1."},
        )

        def sample_func(param1: int) -> bool:
            pass

        schema = ParseUtil._func_to_schema(sample_func)
        self.assertEqual(schema["function"]["name"], "sample_func")
        self.assertEqual(schema["function"]["description"], "Function description")
        self.assertIn("param1", schema["function"]["parameters"]["properties"])
        self.assertEqual(
            schema["function"]["parameters"]["properties"]["param1"]["type"], "number"
        )
        self.assertEqual(
            schema["function"]["parameters"]["properties"]["param1"]["description"],
            "Description of param1.",
        )


if __name__ == "__main__":
    unittest.main()
