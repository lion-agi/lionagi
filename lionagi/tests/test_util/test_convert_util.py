import unittest
import xml.etree.ElementTree as ET

from lionagi.util.convert_util import *


class TestToList(unittest.TestCase):
    def test_with_plain_list(self):
        self.assertEqual(to_list([1, 2, 3]), [1, 2, 3])

    def test_with_nested_list(self):
        self.assertEqual(to_list([1, [2, 3], 4], flatten=True), [1, 2, 3, 4])

    def test_with_nested_list_no_flatten(self):
        self.assertEqual(to_list([1, [2, 3], 4], flatten=False), [1, [2, 3], 4])

    def test_with_tuple(self):
        self.assertEqual(to_list((1, 2, 3)), [1, 2, 3])

    def test_with_set(self):
        input_set = {1, 2, 3}
        result = to_list(input_set)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(set(result), input_set)

    def test_with_dict(self):
        self.assertEqual(to_list({"key": "value"}), [{"key": "value"}])

    def test_with_none_values(self):
        self.assertEqual(to_list([1, None, 2, None], dropna=True), [1, 2])

    def test_with_mixed_types(self):
        self.assertEqual(to_list([1, "two", 3.0]), [1, "two", 3.0])

    def test_with_strings(self):
        self.assertEqual(to_list("string"), ["string"])

    def test_with_bytes(self):
        self.assertEqual(to_list(b"bytes"), [b"bytes"])

    def test_with_bytearray(self):
        self.assertEqual(to_list(bytearray(b"bytearray")), [bytearray(b"bytearray")])


class MyModel(BaseModel):
    id: int
    name: str

class TestToDict(unittest.TestCase):
    def test_with_dict(self):
        """Test conversion of a dict to itself."""
        input_dict = {"key": "value", "number": 42}
        self.assertEqual(to_dict(input_dict), input_dict)

    def test_with_json_string(self):
        """Test conversion of a JSON string to a dict."""
        input_json = '{"key": "value", "number": 42}'
        expected_dict = {"key": "value", "number": 42}
        self.assertEqual(to_dict(input_json), expected_dict)

    def test_with_pandas_series(self):
        """Test conversion of a pandas Series to a dict."""
        input_series = pd.Series([1, 2, 3], index=["a", "b", "c"])
        expected_dict = {"a": 1, "b": 2, "c": 3}
        self.assertEqual(to_dict(input_series), expected_dict)

    def test_with_pandas_dataframe(self):
        """Test conversion of a pandas DataFrame to a dict."""
        input_df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        expected_dict = {"id": [1, 2], "name": ["Alice", "Bob"]}
        self.assertEqual(to_dict(input_df, orient="list"), expected_dict)

    def test_with_pydantic_model(self):
        """Test conversion of a Pydantic model to a dict."""
        model = MyModel(id=1, name="Test Model")
        expected_dict = {"id": 1, "name": "Test Model"}
        self.assertEqual(to_dict(model), expected_dict)


class TestToStr(unittest.TestCase):
    def test_with_dict(self):
        """Test conversion of a dictionary to a JSON-formatted string."""
        input_dict = {"key": "value", "number": 42}
        expected_str = '{"key": "value", "number": 42}'
        # Note: The exact string representation may vary due to key ordering, so consider using json.loads for comparison if needed.
        self.assertEqual(json.loads(to_str(input_dict)), json.loads(expected_str))

    def test_with_string(self):
        """Test conversion of a string to itself."""
        input_str = "This is a test string."
        self.assertEqual(to_str(input_str), input_str)

    def test_with_list(self):
        """Test conversion of a list to a string representation."""
        input_list = [1, 2, 3]
        expected_str = "1, 2, 3"
        self.assertEqual(to_str(input_list), expected_str)

    def test_with_list_as_list(self):
        """Test conversion of a list to its string representation (as a list)."""
        input_list = [1, "two", 3.0]
        expected_str = ['1', 'two', '3.0']
        self.assertEqual(to_str(input_list, as_list=True), expected_str)

    def test_with_pandas_series(self):
        """Test conversion of a pandas Series to a JSON-formatted string."""
        input_series = pd.Series([1, 2, 3], index=["a", "b", "c"])
        # Note: Adjust the expected string as necessary based on the to_str implementation details.
        expected_str = input_series.to_json()
        self.assertEqual(to_str(input_series), expected_str)

    def test_with_pandas_dataframe(self):
        """Test conversion of a pandas DataFrame to a JSON-formatted string."""
        input_df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        # Note: Adjust the expected string as necessary based on the to_str implementation details.
        expected_str = input_df.to_json()
        self.assertEqual(to_str(input_df), expected_str)

    def test_with_pandas_dataframe_as_list(self):
        """Test conversion of a pandas DataFrame to a string representation of a list of dictionaries."""
        input_df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        expected_str = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        self.assertEqual(to_str(input_df, as_list=True), expected_str)


class TestToDf(unittest.TestCase):
    def test_with_list_of_dicts(self):
        """Test converting a list of dictionaries into a DataFrame."""
        input_list = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        expected_df = pd.DataFrame(input_list)
        result_df = to_df(input_list)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_with_series(self):
        """Test converting a pandas Series into a DataFrame."""
        input_series = pd.Series([1, 2, 3], name="numbers")
        expected_df = pd.DataFrame(input_series)
        result_df = to_df(input_series)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_with_dataframe(self):
        """Test that a pandas DataFrame is correctly returned unchanged."""
        input_df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        result_df = to_df(input_df)
        pd.testing.assert_frame_equal(result_df, input_df)

    def test_dropna_and_reset_index(self):
        """Test the dropna and reset_index functionality."""
        input_list = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": None},
            {"name": "Charlie", "age": 25}
        ]
        expected_df = pd.DataFrame([{"name": "Alice", "age": 30.0}, {"name": "Charlie", "age": 25.0}]).reset_index(drop=True)
        result_df = to_df(input_list, how="any", drop_kwargs={"subset": ["age"]}, reset_index=True)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_with_nested_structures(self):
        """Test converting nested structures (list of DataFrames) into a single DataFrame."""
        df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        df2 = pd.DataFrame({"a": [5, 6], "b": [7, 8]})
        input_list = [df1, df2]
        expected_df = pd.concat(input_list).reset_index(drop=True)
        result_df = to_df(input_list, reset_index=True)
        pd.testing.assert_frame_equal(result_df, expected_df)




class TestToNum(unittest.TestCase):
    def test_integer_conversion(self):
        """Test converting string to integer."""
        self.assertEqual(to_num("42"), 42)

    def test_float_conversion(self):
        """Test converting string to float."""
        self.assertEqual(to_num("3.14", num_type=float), 3.14)

    def test_with_upper_bound(self):
        """Test enforcing an upper bound."""
        with self.assertRaises(ValueError):
            to_num("100", upper_bound=50)

    def test_with_lower_bound(self):
        """Test enforcing a lower bound."""
        with self.assertRaises(ValueError):
            to_num("-10", lower_bound=0)

    def test_precision_handling(self):
        """Test handling of precision for float conversions."""
        self.assertEqual(to_num("3.14159", num_type=float, precision=2), 3.14)

    def test_non_numeric_input(self):
        """Test handling of non-numeric input."""
        with self.assertRaises(ValueError):
            to_num("not a number")

    def test_conversion_with_bounds(self):
        """Test converting number within specified bounds."""
        self.assertEqual(to_num("25", upper_bound=100, lower_bound=20), 25)

    def test_conversion_of_actual_number(self):
        """Test converting actual number rather than string."""
        self.assertEqual(to_num(123.456, num_type=float, precision=2), 123.46)






class TestConvertUtil(unittest.TestCase):


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