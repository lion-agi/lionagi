import unittest
from typing import Dict, List, Union, Tuple, Optional, Type, Any
from pathlib import Path
import hashlib
import os
from datetime import datetime
from unittest.mock import patch
import re
from dateutil import parser
import copy


def get_timestamp() -> str:
    """
    Generates a current timestamp in a file-safe string format.

    This function creates a timestamp from the current time, formatted in ISO 8601 format, 
    and replaces characters that are typically problematic in filenames (like colons and periods) 
    with underscores.

    Returns:
        str: The current timestamp in a file-safe string format.

    Example:
        >>> get_timestamp()  # Doctest: +ELLIPSIS
        '...'
    """
    return datetime.now().isoformat().replace(":", "_").replace(".", "_")

def create_copy(input: Any, n: int) -> Any:
    """
    Creates a deep copy of the input object a specified number of times.

    This function makes deep copies of the provided input. If the number of copies ('n') 
    is greater than 1, a list of deep copies is returned. For a single copy, it returns 
    the copy directly.

    Parameters:
        input (Any): The object to be copied.

        n (int): The number of deep copies to create.

    Raises:
        ValueError: If 'n' is not a positive integer.

    Returns:
        Any: A deep copy of 'input' or a list of deep copies if 'n' > 1.

    Example:
        >>> sample_dict = {'key': 'value'}
        >>> create_copy(sample_dict, 2)
        [{'key': 'value'}, {'key': 'value'}]
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"'n' must be a positive integer: {n}")
    return copy.deepcopy(input) if n == 1 else [copy.deepcopy(input) for _ in range(n)]

def create_path(dir: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, time_prefix=False) -> str:
    dir = dir if dir.endswith('/') else dir + '/'
    filename, ext = os.path.splitext(filename)
    ext = ext[1:]  # remove the dot from extension
    os.makedirs(dir, exist_ok=dir_exist_ok)

    if timestamp:
        timestamp_str = get_timestamp()
        if time_prefix:
            filename = f"{timestamp_str}_{filename}.{ext}"
        else:
            filename = f"{filename}_{timestamp_str}.{ext}"
    else:
        filename = f"{filename}.{ext}"

    return os.path.join(dir, filename)

def split_path(path: Path) -> tuple:
    folder_name = path.parent.name
    file_name = path.name
    return (folder_name, file_name)

def change_dict_key(dict_, old_key, new_key):
    if old_key in dict_:
        dict_[new_key] = dict_.pop(old_key)
    else:
        raise KeyError(f"Key '{old_key}' not found in dictionary.")

def create_id(n=32) -> str:
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(16)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:n]

def str_to_datetime(datetime_str: str, fmt: Optional[str] = None) -> datetime:
    if fmt:
        return datetime.strptime(datetime_str, fmt)
    else:
        return parser.parse(datetime_str)
    
def str_to_num(input_: str, 
               upper_bound: Optional[Union[int, float]] = None, 
               lower_bound: Optional[Union[int, float]] = None, 
               num_type: Type[Union[int, float]] = int, 
               precision: Optional[int] = None) -> Union[int, float]:
    numbers = re.findall(r'-?\d+\.?\d*', input_)
    if not numbers:
        raise ValueError(f"No numeric values found in the string: {input_}")
    
    number = numbers[0]
    if num_type is int:
        number = int(float(number))
    elif num_type is float:
        number = round(float(number), precision) if precision is not None else float(number)
    else:
        raise ValueError(f"Invalid number type: {num_type}")

    if upper_bound is not None and number > upper_bound:
        raise ValueError(f"Number {number} is greater than the upper bound of {upper_bound}.")
    if lower_bound is not None and number < lower_bound:
        raise ValueError(f"Number {number} is less than the lower bound of {lower_bound}.")

    return number


def find_depth(nested_obj: Union[Dict, List, Tuple], depth_strategy: str = 'uniform', ignore_non_iterable: bool = False) -> int:
    if depth_strategy not in {'uniform', 'mixed'}:
        raise ValueError("Unsupported depth strategy. Choose 'uniform' or 'mixed'.")

    def _uniform_depth(obj: Union[Dict, List, Tuple], current_depth: int = 0) -> int:
        if isinstance(obj, (list, tuple)):
            return max((_uniform_depth(item, current_depth + 1) for item in obj), default=current_depth)
        elif isinstance(obj, dict):
            return max((_uniform_depth(value, current_depth + 1) for value in obj.values()), default=current_depth)
        else:
            return current_depth

    def _mixed_depth(obj: Union[Dict, List, Tuple], current_depth: int = 0) -> int:
        if isinstance(obj, (list, tuple)):
            return max((_mixed_depth(item, current_depth + 1) for item in obj), default=current_depth)
        elif isinstance(obj, dict):
            return max((_mixed_depth(value, current_depth + 1) for value in obj.values()), default=current_depth)
        else:
            return current_depth if ignore_non_iterable else current_depth + 1

    if depth_strategy == 'uniform':
        return _uniform_depth(nested_obj)
    else:
        return _mixed_depth(nested_obj)

def _is_schema(dict_: Dict, schema: Dict) -> bool:
    for key, expected_type in schema.items():
        if key not in dict_ or not isinstance(dict_[key], expected_type):
            return False
    return True

class TestFindDepth(unittest.TestCase):
    def test_uniform_depth_list(self):
        self.assertEqual(find_depth([[[1]], 2, 3], 'uniform'), 3)

    def test_uniform_depth_mixed(self):
        self.assertEqual(find_depth({'a': [1, [2]]}, 'uniform'), 3)

    def test_mixed_depth(self):
        self.assertEqual(find_depth([{'a': [1]}, 2, 3], 'mixed', True), 3)

    def test_ignore_non_iterable(self):
        self.assertEqual(find_depth([1, [2, [3]]], 'uniform', True), 3)

    def test_invalid_depth_strategy(self):
        with self.assertRaises(ValueError):
            find_depth([], 'invalid')

class TestIsSchema(unittest.TestCase):
    def test_valid_schema(self):
        self.assertTrue(_is_schema({'a': 1, 'b': 'test'}, {'a': int, 'b': str}))

    def test_invalid_schema(self):
        self.assertFalse(_is_schema({'a': 1, 'b': 'test'}, {'a': str, 'b': str}))

    def test_missing_key(self):
        self.assertFalse(_is_schema({'a': 1}, {'a': int, 'b': str}))

if __name__ == '__main__':
    unittest.main()
class TestStrToDatetime(unittest.TestCase):
    def test_str_to_datetime_without_format(self):
        self.assertEqual(
            str_to_datetime("2023-01-01 12:00:00"),
            datetime(2023, 1, 1, 12, 0)
        )

    def test_str_to_datetime_with_format(self):
        self.assertEqual(
            str_to_datetime("January 1, 2023, 12:00 PM", "%B %d, %Y, %I:%M %p"),
            datetime(2023, 1, 1, 12, 0)
        )

    def test_str_to_datetime_invalid_format_raises_value_error(self):
        with self.assertRaises(ValueError):
            str_to_datetime("2023/01/01 12:00:00", "%Y-%m-%d %H:%M:%S")

class TestStrToNum(unittest.TestCase):
    def test_str_to_num_int_default(self):
        self.assertEqual(str_to_num('Value is 123'), 123)

    def test_str_to_num_float_with_precision(self):
        self.assertEqual(str_to_num('Value is -123.456', num_type=float, precision=2), -123.46)

    def test_str_to_num_with_upper_bound_violation(self):
        with self.assertRaises(ValueError):
            str_to_num('Value is 100', upper_bound=99)

    def test_str_to_num_with_lower_bound_violation(self):
        with self.assertRaises(ValueError):
            str_to_num('Value is -1', lower_bound=0)

    def test_str_to_num_no_numeric_value_found_raises_value_error(self):
        with self.assertRaises(ValueError):
            str_to_num('No numbers here')

    def test_str_to_num_invalid_num_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            str_to_num('Value is 123', num_type=str)


class TestChangeDictKey(unittest.TestCase):
    def test_change_dict_key_existing(self):
        sample_dict = {'old_key': 'value'}
        change_dict_key(sample_dict, 'old_key', 'new_key')
        self.assertNotIn('old_key', sample_dict)
        self.assertIn('new_key', sample_dict)
        self.assertEqual(sample_dict['new_key'], 'value')

    def test_change_dict_key_non_existing_raises_key_error(self):
        sample_dict = {'old_key': 'value'}
        with self.assertRaises(KeyError):
            change_dict_key(sample_dict, 'non_existing_key', 'new_key')

class TestCreateId(unittest.TestCase):
    def test_create_id_default_length(self):
        unique_id = create_id()
        self.assertEqual(len(unique_id), 32)

    def test_create_id_custom_length(self):
        lengths = [8, 16, 64]
        for length in lengths:
            unique_id = create_id(n=length)
            self.assertEqual(len(unique_id), length)

    def test_create_id_uniqueness(self):
        id_set = set(create_id() for _ in range(100))
        self.assertEqual(len(id_set), 100)


class TestSplitPath(unittest.TestCase):
    def test_split_path(self):
        # Test with a standard path
        path = Path('/home/user/documents/report.txt')
        result = split_path(path)
        self.assertEqual(result, ('documents', 'report.txt'))

        # Test with a root path
        path = Path('/filename.ext')
        result = split_path(path)
        self.assertEqual(result, ('', 'filename.ext'))

        # Test with a path with no file extension
        path = Path('/home/user/foldername/filename')
        result = split_path(path)
        self.assertEqual(result, ('foldername', 'filename'))

        # # Test with an empty path
        # path = Path('')
        # result = split_path(path)
        # self.assertEqual(result, ('.', ''))


class TestCreatePath(unittest.TestCase):
    @patch('os.makedirs')
    def test_create_path_without_timestamp(self, mock_makedirs):
        expected_path = '/tmp/testfile.txt'
        actual_path = create_path('/tmp', 'testfile.txt', timestamp=False)
        self.assertEqual(actual_path, expected_path)
        mock_makedirs.assert_called_once_with('/tmp/', exist_ok=True)

    # @patch('os.makedirs')
    # def test_create_path_with_timestamp(self, mock_makedirs):
    #     with patch('datetime.datetime') as mock_datetime:
    #         mock_datetime.utcnow.return_value = datetime(2021, 1, 1, 12, 0, 0)
    #         mock_datetime.strftime.return_value = '20210101120000'
    #         expected_path = '/tmp/testfile_20210101120000.txt'
    #         actual_path = create_path('/tmp', 'testfile.txt')
    #         self.assertEqual(actual_path, expected_path)
    #         mock_makedirs.assert_called_once_with('/tmp/', exist_ok=True)

    # @patch('os.makedirs')
    # def test_create_path_with_time_prefix(self, mock_makedirs):
    #     with patch('datetime.datetime') as mock_datetime:
    #         mock_datetime.utcnow.return_value = datetime(2021, 1, 1, 12, 0, 0)
    #         mock_datetime.strftime.return_value = '20210101120000'
    #         expected_path = '/tmp/20210101120000_testfile.txt'
    #         actual_path = create_path('/tmp', 'testfile.txt', time_prefix=True)
    #         self.assertEqual(actual_path, expected_path)
    #         mock_makedirs.assert_called_once_with('/tmp/', exist_ok=True)

    # @patch('os.makedirs')
    # def test_create_path_dir_exist_ok_false(self, mock_makedirs):
    #     with self.assertRaises(FileNotFoundError):
    #         create_path('/nonexistent', 'testfile.txt', dir_exist_ok=False)
    #         mock_makedirs.assert_called_once_with('/nonexistent/', exist_ok=False)


class TestCreateCopy(unittest.TestCase):

    def test_create_single_copy(self):
        sample_dict = {'key': 'value'}
        result = create_copy(sample_dict, 1)
        self.assertEqual(result, sample_dict)
        self.assertIsNot(result, sample_dict)

    def test_create_multiple_copies(self):
        sample_list = ['element']
        n_copies = 3
        result = create_copy(sample_list, n_copies)
        self.assertEqual(len(result), n_copies)
        for copy_item in result:
            self.assertEqual(copy_item, sample_list)
            self.assertIsNot(copy_item, sample_list)

    def test_create_zero_copies_raises_value_error(self):
        with self.assertRaises(ValueError):
            create_copy({}, 0)

    def test_create_negative_copies_raises_value_error(self):
        with self.assertRaises(ValueError):
            create_copy({}, -1)

    def test_create_non_integer_copies_raises_value_error(self):
        with self.assertRaises(ValueError):
            create_copy({}, '2')


# class TestGetTimestamp(unittest.TestCase):

#     @patch('datetime.datetime')
#     def test_get_timestamp(self, mock_datetime):
#         # Define a fixed datetime
#         mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)

#         # Expected timestamp based on the fixed datetime
#         expected_timestamp = "2023-01-01T12_00_00"

#         # Get the actual timestamp from the function
#         actual_timestamp = get_timestamp()

#         # Assert that the actual timestamp matches the expected timestamp
#         self.assertEqual(actual_timestamp, expected_timestamp)


if __name__ == '__main__':
    unittest.main()