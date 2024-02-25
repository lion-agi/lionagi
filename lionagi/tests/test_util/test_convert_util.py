import unittest
import xml.etree.ElementTree as ET

from lionagi.util.convert_util import ConvertUtil


class TestConvertUtil(unittest.TestCase):

    def test_to_dict_with_valid_json(self):
        input_ = '{"key": "value"}'
        expected = {"key": "value"}
        self.assertEqual(ConvertUtil.to_dict(input_), expected)

    def test_to_dict_with_dict(self):
        input_ = {"key": "value"}
        self.assertEqual(ConvertUtil.to_dict(input_), input_)

    def test_to_dict_with_invalid_json(self):
        input_ = '{"key": "value"'
        with self.assertRaises(ValueError):
            ConvertUtil.to_dict(input_)

    def test_to_dict_with_unsupported_type(self):
        input_ = ["key", "value"]
        with self.assertRaises(TypeError):
            ConvertUtil.to_dict(input_)

    def test_is_same_dtype_with_int_list(self):
        input_ = [1, 2, 3]
        self.assertTrue(ConvertUtil.is_same_dtype(input_))

    def test_is_same_dtype_with_str_dict(self):
        input_ = {"a": "apple", "b": "banana"}
        self.assertTrue(ConvertUtil.is_same_dtype(input_))

    def test_is_same_dtype_with_mixed_list(self):
        input_ = [1, "2", 3.0]
        self.assertFalse(ConvertUtil.is_same_dtype(input_))

    def test_is_same_dtype_with_int_list_specifying_float_dtype(self):
        input_ = [1, 2, 3]
        self.assertFalse(ConvertUtil.is_same_dtype(input_, float))


class TestConvertUtilXmlToDict(unittest.TestCase):

    def test_xml_to_dict_with_simple_element(self):
        xml_str = "<root>value</root>"
        root = ET.fromstring(xml_str)
        expected = {"root": "value"}
        self.assertEqual(ConvertUtil.xml_to_dict(root), expected)

    # def test_xml_to_dict_with_children(self):
    #     xml_str = "<root><child1>value1</child1><child2>value2</child2></root>"
    #     root = ET.fromstring(xml_str)
    #     expected = {'root': [{'child1': 'value1'}, {'child2': 'value2'}]}
    #     self.assertEqual(ConvertUtil.xml_to_dict(root), expected)

    def test_xml_to_dict_with_nested_children(self):
        xml_str = "<root><child><subchild>value</subchild></child></root>"
        root = ET.fromstring(xml_str)
        expected = {'root': [['value']]}
        self.assertEqual(ConvertUtil.xml_to_dict(root), expected)

    def test_xml_to_dict_with_multiple_same_tag_children(self):
        xml_str = "<root><child>value1</child><child>value2</child></root>"
        root = ET.fromstring(xml_str)
        expected = {'root': ['value1', 'value2']}
        self.assertEqual(ConvertUtil.xml_to_dict(root), expected)


if __name__ == '__main__':
    unittest.main()