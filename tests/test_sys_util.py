import json
import os
import shutil
import unittest
from typing import Any, Callable, Optional
from unittest.mock import MagicMock

from ..lionagi.utils.sys_util import _flatten_dict, _flatten_list, to_list, str_to_num, make_copy, to_temp, to_csv, hold_call, ahold_call, l_call, al_call, m_call, am_call, e_call, ae_call, get_timestamp, generate_id, make_filepath, to_jsonl


import unittest
from typing import Dict, Any
from collections.abc import Mapping

# Unit test for _flatten_dict function
class TestFlattenDict(unittest.TestCase):
    def test_flatten_dict_simple(self):
        """Test flattening of a simple dictionary."""
        d = {'a': 1, 'b': {'c': 2, 'd': 3}}
        expected_output = [('a', 1), ('b_c', 2), ('b_d', 3)]
        self.assertEqual(list(_flatten_dict(d)), expected_output)

    def test_flatten_dict_nested(self):
        """Test flattening of a nested dictionary."""
        d = {'a': {'b': {'c': {'d': 1}}}}
        expected_output = [('a_b_c_d', 1)]
        self.assertEqual(list(_flatten_dict(d)), expected_output)

    def test_flatten_dict_with_list(self):
        """Test flattening of a dictionary with list values."""
        d = {'a': 1, 'b': [2, {'c': 3}]}
        expected_output = [('a', 1), ('b_0', 2), ('b_1_c', 3)]
        self.assertEqual(list(_flatten_dict(d)), expected_output)

    def test_flatten_dict_with_custom_separator(self):
        """Test flattening of a dictionary with a custom separator."""
        d = {'a': {'b': 1}, 'c': {'d': 2}}
        expected_output = [('a-b', 1), ('c-d', 2)]
        self.assertEqual(list(_flatten_dict(d, sep='-')), expected_output)

    def test_flatten_dict_empty(self):
        """Test flattening of an empty dictionary."""
        d = {}
        expected_output = []
        self.assertEqual(list(_flatten_dict(d)), expected_output)

class TestFlattenList(unittest.TestCase):
    def test_flatten_list_simple(self):
        """Test flattening of a flat list."""
        lst = [1, 2, 3, 4]
        expected_output = [1, 2, 3, 4]
        self.assertEqual(list(_flatten_list(lst)), expected_output)

    def test_flatten_list_nested(self):
        """Test flattening of a nested list."""
        lst = [1, [2, [3, 4]]]
        expected_output = [1, 2, 3, 4]
        self.assertEqual(list(_flatten_list(lst)), expected_output)

    def test_flatten_list_with_none(self):
        """Test flattening of a list containing None."""
        lst = [None, 1, [2, None], [3, [4, None]]]
        expected_output_with_none = [None, 1, 2, None, 3, 4, None]
        expected_output_without_none = [1, 2, 3, 4]
        self.assertEqual(list(_flatten_list(lst, dropna=False)), expected_output_with_none)
        self.assertEqual(list(_flatten_list(lst, dropna=True)), expected_output_without_none)

    def test_flatten_list_empty(self):
        """Test flattening of an empty list."""
        lst = []
        expected_output = []
        self.assertEqual(list(_flatten_list(lst)), expected_output)

    def test_flatten_list_all_none(self):
        """Test flattening of a list with all elements set to None."""
        lst = [None, [None, [None]]]
        expected_output_with_none = [None, None, None]
        expected_output_without_none = []
        self.assertEqual(list(_flatten_list(lst, dropna=False)), expected_output_with_none)
        self.assertEqual(list(_flatten_list(lst, dropna=True)), expected_output_without_none)
        
class TestStrToNum(unittest.TestCase):
    def test_str_to_num_valid_int(self):
        self.assertEqual(str_to_num("42 is the answer"), 42)
    
    def test_str_to_num_valid_float(self):
        self.assertEqual(str_to_num("Pi is approximately 3.14", type_=float), 3.14)

    def test_str_to_num_with_precision(self):
        self.assertEqual(str_to_num("1.2345", type_=float, precision=2), 1.23)

    def test_str_to_num_below_lower_bound(self):
        self.assertEqual(str_to_num("Value is 0", lower_bound=1), "Number 0 is less than the lower bound of 1.")

    def test_str_to_num_above_upper_bound(self):
        self.assertEqual(str_to_num("Value is 200", upper_bound=100), "Number 200 is greater than the upper bound of 100.")

    def test_str_to_num_no_numeric(self):
        with self.assertRaises(ValueError):
            str_to_num("No number here")
    def test_str_to_num_invalid_upper_bound(self):
        with self.assertRaises(ValueError):
            str_to_num("42", upper_bound=-100)

# Unit tests for the make_copy function
class TestMakeCopy(unittest.TestCase):
    def test_make_copy_single(self):
        input_ = {'key': 'value'}
        result = make_copy(input_, n=1)
        self.assertEqual(result, input_)
        self.assertIsNot(result, input_)  # Test that a new object was indeed created

    def test_make_copy_multiple(self):
        input_ = [1, 2, 3]
        n = 3
        results = make_copy(input_, n=n)
        self.assertEqual(len(results), n)
        for item in results:
            self.assertIsNot(item, input_)  # Test that new objects were indeed created

    def test_make_copy_zero(self):
        with self.assertRaises(ValueError):
            make_copy({'key': 'value'}, n=0)
            
    def test_make_copy_negative(self):
        with self.assertRaises(ValueError):
            make_copy({'key': 'value'}, n=-1)
            
    def test_make_copy_non_integer(self):
        with self.assertRaises(ValueError):
            make_copy([1, 2], n='two')
            
class TestToTemp(unittest.TestCase):
    
    def test_to_temp_nested_data(self):
        """Test to_temp with nested data and flags set"""
        input_ = {'a': 1, 'b': {'c': 2, 'd': [3, 4]}}
        result_file = to_temp(input_, flat_dict=True, flat=True)
        # Read the file and compare content
        with open(result_file.name, 'r') as file:
            content = json.load(file)
        expected = [{'a': 1}, {'b_c': 2}, {'b_d_0': 3}, {'b_d_1': 4}]
        self.assertEqual(content, expected)
        os.unlink(result_file.name)  # Cleanup
    
    def test_to_temp_non_serializable_data(self):
        """Test to_temp with non JSON serializable data"""
        input_ = {'a': 1, 'b': [2, 3], 'c': set([4])}  # set is not JSON serializable
        with self.assertRaises(TypeError):
            to_temp(input_)
            
class TestToCSV(unittest.TestCase):
    # Directory for temporary files
    temp_dir = 'test_to_csv_dir'

    def setUp(self):
        # Create a new directory
        os.makedirs(self.temp_dir, exist_ok=True)

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_to_csv_with_output(self):
        data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        filename = os.path.join(self.temp_dir, 'output.csv')
        result = to_csv(data, filename, out=True)
        self.assertEqual(result, data)

    def test_to_csv_without_output(self):
        data = [{'name': 'Charlie', 'age': 35}]
        filename = os.path.join(self.temp_dir, 'output2.csv')
        result = to_csv(data, filename)
        self.assertIsNone(result)
    
    def test_to_csv_create_directory(self):
        data = [{'name': 'Dave', 'age': 40}]
        nested_dir = os.path.join(self.temp_dir, 'nested')
        filename = os.path.join(nested_dir, 'output3.csv')
        result = to_csv(data, filename, file_exist_ok=True, out=True)
        self.assertTrue(os.path.exists(nested_dir))
        self.assertEqual(result, data)
        # Cleanup nested directory
        shutil.rmtree(nested_dir, ignore_errors=True)

    def test_to_csv_no_directory(self):
        data = [{'name': 'Eve', 'age': 28}]
        # An intentionally wrong directory that doesn't exist
        filename = '/non_existent_directory/output4.csv'
        with self.assertRaises(FileNotFoundError):
            to_csv(data, filename)
            
# Unit tests for the hold_call function
class TestHoldCall(unittest.TestCase):
    def test_hold_call_executes_successfully(self):
        """Test that hold_call executes the function properly and returns its result."""
        mock_func = MagicMock(return_value="success")
        result = hold_call(("input",), func_=mock_func, hold=0)  # hold is set to 0 for quick test
        mock_func.assert_called_once_with("input")
        self.assertEqual(result, "success")

    def test_hold_call_handles_exception(self):
        """Test that hold_call prints message and raises exception when ignore is False."""
        mock_func = MagicMock(side_effect=Exception("test exception"))
        
        with self.assertRaises(Exception) as context:
            hold_call(("input",), func_=mock_func, hold=0, ignore=False)

        self.assertIn("test exception", str(context.exception))
        

    def test_hold_call_message_on_exception(self):
        """Test that hold_call prints custom message on exception when provided."""
        mock_func = MagicMock(side_effect=Exception('custom error'))
        with self.assertRaises(Exception):
            hold_call(('input',), func_=mock_func, msg="Custom Message", hold=0)


# Unit tests for the l_call function
class TestLCall(unittest.TestCase):
    def test_l_call_valid_input(self):
        """Test that l_call applies the function to each element in the list."""
        input_ = [1, 2, 3]
        func_ = lambda x: x * 2
        expected_output = [2, 4, 6]
        self.assertEqual(l_call(input_, func_), expected_output)

    def test_l_call_with_none(self):
        """Test l_call with None values and dropna=True."""
        input_ = [1, 3]
        func_ = lambda x: x * 2
        expected_output = [2, 6]  # None is dropped
        self.assertEqual(l_call(input_, func_), expected_output)
    
    def test_l_call_func_raises(self):
        """Test l_call raises an error if the function cannot be applied to the input."""
        input_ = [1, 2, 3]
        func_ = lambda x: x / 0  # This will raise an exception
        with self.assertRaises(ValueError):
            l_call(input_, func_)

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)