import unittest
from lionagi.utils.convert_util import *

# Test cases for the function
class TestStrToNum(unittest.TestCase):
    def test_valid_int(self):
        self.assertEqual(str_to_num("123"), 123)
        self.assertEqual(str_to_num("-123"), -123)
    
    def test_valid_float(self):
        self.assertEqual(str_to_num("123.45", num_type=float), 123.45)
        self.assertEqual(str_to_num("-123.45", num_type=float), -123.45)
    
    def test_precision(self):
        self.assertEqual(str_to_num("123.456", num_type=float, precision=1), 123.5)
        self.assertEqual(str_to_num("123.444", num_type=float, precision=2), 123.44)
    
    def test_bounds(self):
        self.assertEqual(str_to_num("10", lower_bound=5, upper_bound=15), 10)
        with self.assertRaises(ValueError):
            str_to_num("20", upper_bound=15)
        with self.assertRaises(ValueError):
            str_to_num("2", lower_bound=5)
    
    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            str_to_num("abc")
        with self.assertRaises(ValueError):
            str_to_num("123abc", num_type=str)
    
    def test_no_numeric_value(self):
        with self.assertRaises(ValueError):
            str_to_num("No numbers here")



# Functions to be tested
def dict_to_xml(data: Dict[str, Any], root_tag: str = 'node') -> str:
    root = ET.Element(root_tag)
    _build_xml(root, data)
    return ET.tostring(root, encoding='unicode')

def _build_xml(element: ET.Element, data: Any):
    if isinstance(data, dict):
        for key, value in data.items():
            sub_element = ET.SubElement(element, key)
            _build_xml(sub_element, value)
    elif isinstance(data, list):
        for item in data:
            item_element = ET.SubElement(element, 'item')
            _build_xml(item_element, item)
    else:
        element.text = str(data)

def xml_to_dict(element: ET.Element) -> Dict[str, Any]:
    dict_data = {}
    for child in element:
        if list(child):
            dict_data[child.tag] = xml_to_dict(child)
        else:
            dict_data[child.tag] = child.text
    return dict_data

# Test cases for the functions
class TestDictXMLConversion(unittest.TestCase):
    def setUp(self):
        self.data = {
            'name': 'John',
            'age': 30,
            'children': [
                {'name': 'Alice', 'age': 5},
                {'name': 'Bob', 'age': 7}
            ]
        }
        self.root_tag = 'person'
        self.xml = dict_to_xml(self.data, self.root_tag)
        self.xml_element = ET.fromstring(self.xml)

    def test_dict_to_xml(self):
        self.assertIn('<name>John</name>', self.xml)
        self.assertIn('<age>30</age>', self.xml)
        self.assertIn('<children>', self.xml)
        self.assertIn('<item>', self.xml)

    # def test_xml_to_dict(self):
    #     data_from_xml = xml_to_dict(self.xml_element)
    #     self.assertEqual(data_from_xml, self.data)

    # def test_xml_to_dict_to_xml(self):
    #     data_from_xml = xml_to_dict(self.xml_element)
    #     xml_from_dict = dict_to_xml(data_from_xml, self.root_tag)
    #     self.assertEqual(xml_from_dict, self.xml)

    # def test_invalid_input(self):
    #     with self.assertRaises(TypeError):
    #         dict_to_xml("not a dict", self.root_tag)



class TestDocstringExtraction(unittest.TestCase):
    def test_google_style_extraction(self):
        def sample_func(arg1, arg2):
            """
            This is a sample function.

            Args:
                arg1 (int): The first argument.
                arg2 (str): The second argument.

            Returns:
                bool: The truth value.
            """
            return True

        description, params = extract_docstring_details_google(sample_func)
        self.assertEqual(description, "This is a sample function.")
        self.assertEqual(params, {
            'arg1': 'The first argument.',
            'arg2': 'The second argument.'
        })

    def test_rest_style_extraction(self):
        def sample_func(arg1, arg2):
            """
            This is a sample function.

            :param int arg1: The first argument.
            :param str arg2: The second argument.
            :return: The truth value.
            :rtype: bool
            """
            return True

        description, params = extract_docstring_details_rest(sample_func)
        self.assertEqual(description, "This is a sample function.")
        self.assertEqual(params, {
            'arg1': 'The first argument.',
            'arg2': 'The second argument.'
        })

    def test_extract_docstring_details_with_invalid_style(self):
        def sample_func(arg1, arg2):
            return True

        with self.assertRaises(ValueError):
            extract_docstring_details(sample_func, style='unsupported')

class TestPythonToJsonTypeConversion(unittest.TestCase):
    def test_python_to_json_type_conversion(self):
        self.assertEqual(python_to_json_type('str'), 'string')
        self.assertEqual(python_to_json_type('int'), 'number')
        self.assertEqual(python_to_json_type('float'), 'number')
        self.assertEqual(python_to_json_type('list'), 'array')
        self.assertEqual(python_to_json_type('tuple'), 'array')
        self.assertEqual(python_to_json_type('bool'), 'boolean')
        self.assertEqual(python_to_json_type('dict'), 'object')
        self.assertEqual(python_to_json_type('nonexistent'), 'object')

class TestFunctionToSchema(unittest.TestCase):
    def test_func_to_schema(self):
        def sample_func(arg1: int, arg2: str) -> bool:
            """
            This is a sample function.

            Args:
                arg1 (int): The first argument.
                arg2 (str): The second argument.

            Returns:
                bool: The truth value.
            """
            return True

        schema = func_to_schema(sample_func, style='google')
        expected_schema = {
            "type": "function",
            "function": {
                "name": "sample_func",
                "description": "This is a sample function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "arg1": {
                            "type": "number",
                            "description": "The first argument."
                        },
                        "arg2": {
                            "type": "string",
                            "description": "The second argument."
                        }
                    },
                    "required": ["arg1", "arg2"]
                }
            }
        }
        self.assertEqual(schema, expected_schema)

if __name__ == '__main__':
    unittest.main()
    
    
# --------------------------------------------------