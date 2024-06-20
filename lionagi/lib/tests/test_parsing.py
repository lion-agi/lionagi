from lionagi.lib.parsers import *
import unittest
from lionagi.lib.parsers.md_to_json import escape_chars_in_json
from lionagi.lib.parsers.extract_docstring import (
    _extract_docstring_details_google,
    _extract_docstring_details_rest,
)


class TestChooseMostSimilar(unittest.TestCase):
    def test_choose_most_similar_default(self):
        word = "helo"
        correct_words_list = ["hello", "help", "hero", "hill"]
        result = choose_most_similar(word, correct_words_list)
        self.assertEqual(result, "hello")

    def test_choose_most_similar_custom_func(self):
        def dummy_similarity(a, b):
            return 1.0 if a == b else 0.0

        word = "test"
        correct_words_list = ["test", "toast", "taste"]
        result = choose_most_similar(
            word, correct_words_list, score_func=dummy_similarity
        )
        self.assertEqual(result, "test")

    def test_choose_most_similar_empty_list(self):
        word = "test"
        correct_words_list = []
        result = choose_most_similar(word, correct_words_list)
        self.assertIsNone(result)

    def test_choose_most_similar_no_score_func(self):
        word = "world"
        correct_words_list = ["word", "worn", "wild"]
        result = choose_most_similar(word, correct_words_list)
        self.assertIn(
            result, correct_words_list
        )  # Since the default function is used, any close match is acceptable.


class TestExtractCodeBlocks(unittest.TestCase):
    def test_extract_python_code(self):
        input_text = (
            "Here is some Python code:\n```python\nprint('Hello, world!')\n```\n"
        )
        expected_output = "print('Hello, world!')"
        self.assertEqual(extract_code_blocks(input_text), expected_output)

    def test_extract_java_code(self):
        input_text = "Here is some Java code:\n```java\nSystem.out.println('Hello, world!');\n```\n"
        expected_output = "System.out.println('Hello, world!');"
        self.assertEqual(extract_code_blocks(input_text), expected_output)

    def test_extract_javascript_code(self):
        input_text = "Here is some JavaScript code:\n```javascript\nconsole.log('Hello, world!');\n```\n"
        expected_output = "console.log('Hello, world!');"
        self.assertEqual(extract_code_blocks(input_text), expected_output)

    def test_extract_cpp_code(self):
        input_text = "Here is some C++ code:\n```cpp\n#include <iostream>\nint main() { std::cout << 'Hello, world!'; return 0; }\n```\n"
        expected_output = "#include <iostream>\nint main() { std::cout << 'Hello, world!'; return 0; }"
        self.assertEqual(extract_code_blocks(input_text), expected_output)

    def test_extract_ruby_code(self):
        input_text = "Here is some Ruby code:\n```ruby\nputs 'Hello, world!'\n```\n"
        expected_output = "puts 'Hello, world!'"
        self.assertEqual(extract_code_blocks(input_text), expected_output)


class TestExtractDocstringDetails(unittest.TestCase):

    def test_extract_google_style(self):
        def sample_func():
            """
            Sample function.

            Args:
                    param1 (int): Description of param1.
                    param2 (str): Description of param2.
            """
            pass

        description, params = _extract_docstring_details_google(sample_func)
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

        description, params = _extract_docstring_details_rest(sample_func)
        self.assertEqual(description, "Sample function.")
        self.assertDictEqual(
            params,
            {"param1": "Description of param1.", "param2": "Description of param2."},
        )

    def test_google_style(self):
        def example_function(param1: int, param2: str):
            """
            Example function.

            Args:
                param1 (int): The first parameter.
                param2 (str): The second parameter.
            """
            pass

        description, params = extract_docstring_details(
            example_function, style="google"
        )
        self.assertEqual(description, "Example function.")
        self.assertEqual(
            params,
            {"param1": "The first parameter.", "param2": "The second parameter."},
        )

    def test_rest_style(self):
        def example_function(param1: int, param2: str):
            """
            Example function.

            :param param1: The first parameter.
            :type param1: int
            :param param2: The second parameter.
            :type param2: str
            """
            pass

        description, params = extract_docstring_details(example_function, style="rest")
        self.assertEqual(description, "Example function.")
        self.assertEqual(
            params,
            {"param1": "The first parameter.", "param2": "The second parameter."},
        )

    def test_no_docstring(self):
        def example_function(param1: int, param2: str):
            pass

        description, params = extract_docstring_details(
            example_function, style="google"
        )
        self.assertEqual(description, None)
        self.assertEqual(params, {})

    def test_unsupported_style(self):
        def example_function(param1: int, param2: str):
            """
            Example function.

            Args:
                param1 (int): The first parameter.
                param2 (str): The second parameter.
            """
            pass

        with self.assertRaises(ValueError):
            extract_docstring_details(example_function, style="unsupported")

    def test_google_style_incomplete(self):
        def example_function(param1: int, param2: str):
            """
            Example function.

            Args:
                param1: The first parameter.
                param2 (str):
            """
            pass

        description, params = extract_docstring_details(
            example_function, style="google"
        )
        self.assertEqual(description, "Example function.")
        self.assertEqual(params, {"param1": "The first parameter.", "param2": ""})


class TestForceValidateBoolean(unittest.TestCase):
    def test_boolean_true(self):
        self.assertTrue(force_validate_boolean(True))
        self.assertTrue(force_validate_boolean("true"))
        self.assertTrue(force_validate_boolean("1"))
        self.assertTrue(force_validate_boolean("yes"))
        self.assertTrue(force_validate_boolean("correct"))

    def test_boolean_false(self):
        self.assertFalse(force_validate_boolean(False))
        self.assertFalse(force_validate_boolean("false"))
        self.assertFalse(force_validate_boolean("0"))
        self.assertFalse(force_validate_boolean("no"))
        self.assertFalse(force_validate_boolean("incorrect"))
        self.assertFalse(force_validate_boolean("none"))
        self.assertFalse(force_validate_boolean("n/a"))

    def test_invalid_conversion(self):
        try:
            force_validate_boolean("invalid")
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        try:
            force_validate_boolean(123)
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        try:
            force_validate_boolean(None)
        except Exception as e:
            self.assertIsInstance(e, ValueError)

    def test_strip_whitespace(self):
        self.assertTrue(force_validate_boolean("  true  "))
        self.assertFalse(force_validate_boolean("  false  "))

    def test_case_insensitive(self):
        self.assertTrue(force_validate_boolean("TRUE"))
        self.assertTrue(force_validate_boolean("Yes"))
        self.assertFalse(force_validate_boolean("FALSE"))
        self.assertFalse(force_validate_boolean("No"))


class TestForceValidateKeys2(unittest.TestCase):
    def test_exact_match(self):
        keys = ["name", "age", "location"]
        input_dict = {"name": "John", "age": 30, "location": "New York"}
        expected_output = {"name": "John", "age": 30, "location": "New York"}
        self.assertEqual(force_validate_keys(input_dict, keys), expected_output)

    def test_partial_match(self):
        keys = ["name", "age", "location"]
        input_dict = {"nme": "John", "ag": 30, "loc": "New York"}
        expected_output = {"name": "John", "age": 30, "location": "New York"}
        self.assertEqual(force_validate_keys(input_dict, keys), expected_output)

    def test_additional_keys(self):
        keys = ["name", "age"]
        input_dict = {"name": "John", "age": 30, "location": "New York"}
        expected_output = {"name": "John", "age": 30, "location": "New York"}
        self.assertEqual(force_validate_keys(input_dict, keys), expected_output)

    def test_missing_keys(self):
        keys = ["name", "age", "location"]
        input_dict = {"name": "John"}
        expected_output = {"name": "John"}
        self.assertEqual(force_validate_keys(input_dict, keys), expected_output)

    def test_custom_score_func(self):
        def dummy_similarity(a, b):
            return 1.0 if a == b else 0.0

        keys = ["name", "age", "location"]
        input_dict = {"name": "John", "age": 30, "loc": "New York"}
        expected_output = {"name": "John", "age": 30, "location": "New York"}
        self.assertEqual(
            force_validate_keys(input_dict, keys, score_func=dummy_similarity),
            expected_output,
        )


class TestForceValidateKeys(unittest.TestCase):
    def test_match_mode(self):
        keys = ["name", "age", "location"]
        dict_ = {"name": "John", "age": 30, "loc": "NYC"}
        result = force_validate_keys(dict_, keys)
        self.assertEqual(result, {"name": "John", "age": 30, "location": "NYC"})

    def test_superset_mode(self):
        keys = ["name", "age"]
        dict_ = {"name": "John", "age": 30, "location": "NYC"}
        result = force_validate_keys(dict_, keys)
        self.assertEqual(result, {"name": "John", "age": 30, "location": "NYC"})

    def test_subset_mode(self):
        keys = ["name", "age", "location"]
        dict_ = {"name": "John", "age": 30}
        result = force_validate_keys(dict_, keys)
        self.assertEqual(result, {"name": "John", "age": 30})

    def test_handle_unmatched_ignore(self):
        keys = ["name", "age"]
        dict_ = {"name": "John", "age": 30, "location": "NYC"}
        result = force_validate_keys(dict_, keys, handle_unmatched="ignore")
        self.assertEqual(result, {"name": "John", "age": 30, "location": "NYC"})

    def test_handle_unmatched_force(self):
        keys = ["name", "age", "location"]
        dict_ = {"name": "John", "age": 30}
        result = force_validate_keys(
            dict_, keys, handle_unmatched="force", fill_value="Unknown"
        )
        self.assertEqual(result, {"name": "John", "age": 30, "location": "Unknown"})

    def test_handle_unmatched_remove(self):
        keys = ["name", "age"]
        dict_ = {"name": "John", "age": 30, "location": "NYC"}
        result = force_validate_keys(dict_, keys, handle_unmatched="remove")
        self.assertEqual(result, {"name": "John", "age": 30})

    def test_handle_unmatched_raise(self):
        keys = ["name", "age", "location"]
        dict_ = {"name": "John", "age": 30}
        with self.assertRaises(ValueError):
            force_validate_keys(dict_, keys, handle_unmatched="raise")

    def test_handle_unmatched_fill(self):
        keys = ["name", "age", "location"]
        dict_ = {"name": "John", "age": 30}
        result = force_validate_keys(
            dict_, keys, handle_unmatched="fill", fill_value="Unknown"
        )
        self.assertEqual(result, {"name": "John", "age": 30, "location": "Unknown"})

    def test_empty_dict(self):
        keys = ["name", "age", "location"]
        dict_ = {}
        result = force_validate_keys(
            dict_, keys, handle_unmatched="fill", fill_value="Unknown"
        )
        self.assertEqual(
            result, {"name": "Unknown", "age": "Unknown", "location": "Unknown"}
        )

    def test_empty_keys(self):
        keys = []
        dict_ = {"name": "John", "age": 30, "location": "NYC"}
        result = force_validate_keys(dict_, keys)
        self.assertEqual(result, {"name": "John", "age": 30, "location": "NYC"})

    def test_custom_score_func(self):
        def custom_score_func(a, b):
            return len(set(a) & set(b)) / len(set(a) | set(b))

        keys = ["name", "age", "location"]
        dict_ = {"name": "John", "age": 30, "loc": "NYC"}
        result = force_validate_keys(dict_, keys, score_func=custom_score_func)
        self.assertEqual(result, {"name": "John", "age": 30, "location": "NYC"})

    def test_no_matching_keys(self):
        keys = ["gender", "nationality"]
        dict_ = {"name": "John", "age": 30, "location": "NYC"}

        try:
            result = force_validate_keys(
                dict_, keys, handle_unmatched="force", fill_value="Unknown", strict=True
            )
            self.assertEqual(
                result, {"gender": 30, "nationality": "John", "location": "NYC"}
            )
        except Exception as e:
            self.assertIsInstance(e, ValueError)

    def test_keys_as_dict(self):
        keys = {"name": str, "age": int, "location": str}
        dict_ = {"name": "John", "age": 30, "loc": "NYC"}
        result = force_validate_keys(dict_, keys)
        self.assertEqual(result, {"name": "John", "age": 30, "location": "NYC"})

    def test_fill_value_with_different_types(self):
        keys = ["name", "age", "is_student"]
        dict_ = {"name": "John"}
        fill_mapping = {"age": 0, "is_student": False}
        result = force_validate_keys(
            dict_, keys, handle_unmatched="fill", fill_mapping=fill_mapping
        )
        self.assertEqual(result, {"name": "John", "age": 0, "is_student": False})

    def test_case_insensitive_matching(self):
        keys = ["Name", "Age", "Location"]
        dict_ = {"name": "John", "age": 30, "location": "NYC"}
        result = force_validate_keys(dict_, keys)
        self.assertEqual(result, {"Name": "John", "Age": 30, "Location": "NYC"})

    def test_special_characters(self):
        keys = ["name", "age", "email"]
        dict_ = {"name": "John", "age": 30, "email_address": "john@example.com"}
        result = force_validate_keys(dict_, keys)
        self.assertEqual(
            result, {"name": "John", "age": 30, "email": "john@example.com"}
        )

    def test_nested_dictionaries(self):
        keys = ["name", "age", "address"]
        dict_ = {
            "name": "John",
            "age": 30,
            "location": {"city": "New York", "country": "USA"},
        }
        result = force_validate_keys(dict_, keys)
        self.assertEqual(
            result,
            {
                "name": "John",
                "age": 30,
                "address": {"city": "New York", "country": "USA"},
            },
        )


class TestMdToJson(unittest.TestCase):
    def test_valid_markdown_json(self):
        md_content = """
        Here is a JSON example:
        ```json
        {"key": "value"}
        ```
        """
        self.assertEqual(md_to_json(md_content), {"key": "value"})

    def test_missing_keys(self):
        md_content = """
        ```json
        {"key": "value"}
        ```
        """
        with self.assertRaises(ValueError) as cm:
            md_to_json(md_content, expected_keys=["missing_key"])
        self.assertEqual(
            str(cm.exception), "Missing expected keys in JSON object: missing_key"
        )

    def test_custom_parser(self):
        def custom_parser(json_str):
            return {"parsed": True}

        md_content = """
        ```json
        {"key": "value"}
        ```
        """
        self.assertEqual(md_to_json(md_content, parser=custom_parser), {"parsed": True})

    def test_no_json_block(self):
        md_content = """
        Here is some text without a JSON block.
        """
        with self.assertRaises(ValueError) as cm:
            md_to_json(md_content)
        self.assertEqual(
            str(cm.exception), "No JSON code block found in the Markdown content."
        )


class TestEscapeCharsInJson(unittest.TestCase):
    def test_escape_default_chars(self):
        self.assertEqual(
            escape_chars_in_json('{"key": "value\n"}'), '{"key": "value\\n"}'
        )

    def test_custom_char_map(self):
        custom_map = {"\n": "\\n", "\r": "\\r"}
        self.assertEqual(
            escape_chars_in_json('{"key": "value\r\n"}', char_map=custom_map),
            '{"key": "value\\r\\n"}',
        )


class TestExtractJsonBlock(unittest.TestCase):
    def test_extract_json_block(self):
        md_content = """
        ```json
        {
            "key": "value", 
            "key2": ["value1", "value2"], 
            "key3": {"nested_key": "nested_value"}
        }
        ```
        """
        self.assertEqual(
            extract_json_block(md_content),
            {
                "key": "value",
                "key2": ["value1", "value2"],
                "key3": {"nested_key": "nested_value"},
            },
        )

    def test_no_json_block(self):
        md_content = """
        Here is some text without a JSON block.
        """
        with self.assertRaises(ValueError) as cm:
            extract_json_block(md_content)
        self.assertEqual(
            str(cm.exception), "No JSON code block found in the Markdown content."
        )

    def test_malformed_json_block(self):
        md_content = """
        ```json
        {"key": "value"
        ```
        """
        self.assertEqual(extract_json_block(md_content), {"key": "value"})

    def test_multiple_json_blocks(self):
        md_content = """
        ```json
        {"key1": "value1"}
        ```
        Some text in between.
        ```json
        {"key2": "value2"}
        ```
        """
        self.assertEqual(extract_json_block(md_content), {"key1": "value1"})

    def test_md_to_json(self):
        """Test extracting and validating JSON from Markdown content."""
        markdown = '```json\n{"key": "value"}\n```'
        result = md_to_json(markdown, expected_keys=["key"])
        self.assertEqual(result, {"key": "value"})
        with self.assertRaises(ValueError):
            md_to_json(markdown, expected_keys=["missing_key"])


class TestFuzzyParseJson(unittest.TestCase):
    def test_valid_json(self):
        self.assertEqual(fuzzy_parse_json('{"key": "value"}'), {"key": "value"})

    def test_single_quotes(self):
        self.assertEqual(fuzzy_parse_json("{'key': 'value'}"), {"key": "value"})

    def test_fix_brackets(self):
        self.assertEqual(fuzzy_parse_json('{"key": "value"'), {"key": "value"})

    def test_invalid_json(self):
        with self.assertRaises(ValueError):
            fuzzy_parse_json('{"key": "value",}')

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            fuzzy_parse_json("")

    def test_incomplete_json(self):
        with self.assertRaises(ValueError):
            fuzzy_parse_json('{"key": ')

    def test_array_json(self):
        self.assertEqual(fuzzy_parse_json('["value1", "value2"]'), ["value1", "value2"])

    def test_nested_json(self):
        self.assertEqual(
            fuzzy_parse_json('{"key": {"nested_key": "nested_value"}}'),
            {"key": {"nested_key": "nested_value"}},
        )

    def test_extra_closing_bracket(self):
        with self.assertRaises(ValueError):
            fuzzy_parse_json('{"key": "value"}}')

    def test_missing_opening_bracket(self):
        with self.assertRaises(ValueError):
            fuzzy_parse_json('"key": "value"}')

    def test_mismatched_brackets(self):
        with self.assertRaises(ValueError):
            fuzzy_parse_json('{"key": [1, 2, 3}')

    def test_strict_mode(self):
        self.assertEqual(fuzzy_parse_json("{'key': 'value'}"), {"key": "value"})

    def test_basic_json_parsing(self):
        """Test parsing of correctly formatted JSON strings."""
        json_str = '{"name": "John", "age": 30}'
        expected = {"name": "John", "age": 30}
        self.assertEqual(fuzzy_parse_json(json_str), expected)

    def test_missing_closing_brackets(self):
        """Test JSON strings missing various closing brackets."""
        test_cases = [
            ('{"name": "John", "age": 30', {"name": "John", "age": 30}),
            ('[{"name": "John", "age": 30}', [{"name": "John", "age": 30}]),
            ('{"people": [{"name": "John"', {"people": [{"name": "John"}]}),
        ]
        for json_str, expected in test_cases:
            with self.subTest(json_str=json_str):
                self.assertEqual(fuzzy_parse_json(json_str), expected)

    def test_nested_structures(self):
        """Test with nested JSON objects and arrays."""
        json_str = '{"data": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"'
        expected = {"data": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]}
        self.assertEqual(fuzzy_parse_json(json_str), expected)

    def test_strict_mode(self):
        """Test the function's behavior in strict mode."""
        correct_json_str = '{"name": "John", "age": 30}'
        malformed_json_str = '{"name": "John", "age": 30'
        # Should work fine with correct JSON
        self.assertEqual(
            fuzzy_parse_json(correct_json_str),
            {"name": "John", "age": 30},
        )

    def test_error_handling(self):
        """Test with irreparably malformed JSON."""
        json_str = '{"name": "John", "age": 30 something wrong}'
        with self.assertRaises(ValueError):
            fuzzy_parse_json(json_str)


class TestForceValidateMapping(unittest.TestCase):

    def test_valid_json_string(self):
        keys = ["key1", "key2"]
        input_str = '{"key1": "value1", "key2": "value2"}'

        result = force_validate_mapping(input_str, keys)
        expected = {"key1": "value1", "key2": "value2"}
        self.assertEqual(result, expected)

    def test_single_quotes_json(self):
        keys = ["key1", "key2"]
        input_str = "{'key1': 'value1', 'key2': 'value2'}"

        result = force_validate_mapping(input_str, keys)
        expected = {"key1": "value1", "key2": "value2"}
        self.assertEqual(result, expected)

    def test_already_valid_dict(self):
        keys = ["key1", "key2"]
        input_dict = {"key1": "value1", "key2": "value2"}

        result = force_validate_mapping(input_dict, keys)
        expected = {"key1": "value1", "key2": "value2"}
        self.assertEqual(result, expected)

    def test_invalid_md_invalid_json(self):
        keys = ["key1", "key2"]
        input_str = """
        key1: value1,
        key2: value2,
        """
        with self.assertRaises(ValueError):
            force_validate_mapping(input_str, keys)

    def test_missing_keys(self):
        keys = ["key1", "key3"]
        input_str = '{"key1": "value1", "key2": "value2"}'

        with self.assertRaises(ValueError):
            force_validate_mapping(input_str, keys, strict=True)

    def test_extra_keys_in_input(self):
        keys = ["key1", "key2"]
        input_str = '{"key1": "value1", "key2": "value2", "key3": "value3"}'

        result = force_validate_mapping(input_str, keys, handle_unmatched="remove")
        expected = {"key1": "value1", "key2": "value2"}
        self.assertEqual(result, expected)

    def test_no_conversion_needed(self):
        keys = {"key1": "integer", "key2": "string"}
        input_dict = {"key1": 1, "key2": "value2"}

        result = force_validate_mapping(input_dict, keys)
        expected = {"key1": 1, "key2": "value2"}
        self.assertEqual(result, expected)

    def test_empty_input(self):
        keys = ["key1", "key2"]
        input_str = ""

        with self.assertRaises(ValueError):
            force_validate_mapping(input_str, keys)


if __name__ == "__main__":
    unittest.main()
