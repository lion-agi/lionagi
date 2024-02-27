from lionagi.core.action.util import _extract_docstring_details_google, \
    _extract_docstring_details_rest, _func_to_schema, func_to_tool
from lionagi.core.schema import Tool

import unittest
from unittest.mock import patch


class TestExtractDocstringDetailsGoogle(unittest.TestCase):

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
        self.assertDictEqual(params, {"param1": "Description of param1.", "param2": "Description of param2."})


class TestExtractDocstringDetailsRest(unittest.TestCase):

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
        self.assertDictEqual(params, {"param1": "Description of param1.", "param2": "Description of param2."})


class TestFuncToSchema(unittest.TestCase):

    @patch('lionagi.core.action.util._extract_docstring_details')
    def test_func_to_schema(self, mock_extract):
        mock_extract.return_value = ("Function description", {"param1": "Description of param1."})

        def sample_func(param1: int) -> bool:
            pass

        schema = _func_to_schema(sample_func)
        self.assertEqual(schema['function']['name'], 'sample_func')
        self.assertEqual(schema['function']['description'], 'Function description')
        self.assertIn('param1', schema['function']['parameters']['properties'])
        self.assertEqual(schema['function']['parameters']['properties']['param1']['type'], 'number')
        self.assertEqual(schema['function']['parameters']['properties']['param1']['description'],
                         'Description of param1.')


class TestFuncToTool(unittest.TestCase):

    def test_func_to_tool(self):
        def sample_func(param1: int) -> bool:
            """Sample function.

            Args:
                param1 (int): Description of param1.

            Returns:
                bool: Description of return value.
            """
            return True

        tool = func_to_tool(sample_func)
        self.assertIsInstance(tool, Tool)
        self.assertEqual(tool.func, sample_func)
        self.assertTrue('function' in tool.schema_)


if __name__ == '__main__':
    unittest.main()