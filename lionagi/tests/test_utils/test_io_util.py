import unittest
import json
import os
from unittest.mock import mock_open, patch
from io import StringIO
from lionagi.utils.io_util import IOUtil


class NonClosingStringIO(StringIO):
    def close(self):
        # Override close method to keep StringIO open
        pass


class TestIOUtil(unittest.TestCase):

    def setUp(self):
        self.valid_data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        self.empty_data = []
        self.mock_csv_data = "name,age\nAlice,30\nBob,25"
        self.expected_output = [{'name': 'Alice', 'age': '30'}, {'name': 'Bob', 'age': '25'}]
        self.valid_jsonl_data = '{"name": "Alice", "age": 30}\n{"name": "Bob", "age": 25}\n'
        self.expected_valid_output = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        self.invalid_json_data = '{"name": "Alice", "age": 30}\nInvalid JSON\n{"name": "Bob", "age": 25}\n'
        self.valid_json_data = '{"name": "Alice", "age": 30}'
        self.invalid_json_data = '{name: Alice, age: 30}'
        self.csv_data1 = "name,age\nAlice,30\nBob,25"
        self.csv_data2 = "name,score\nAlice,85\nBob,90"
        self.merged_data = "name,age,score\nAlice,30,85\nBob,25,90"
        self.empty_data = ""
        self.expected_csv = "name,age\nAlice,30\nBob,25\n"

    @patch("builtins.open", new_callable=mock_open, read_data="name,age\nAlice,30\nBob,25")
    def test_read_csv_valid_file(self, mock_file):
        result = IOUtil.read_csv("dummy.csv")
        self.assertEqual(result, self.expected_output)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_read_csv_nonexistent_file(self, mock_file):
        with self.assertRaises(FileNotFoundError):
            IOUtil.read_csv("nonexistent.csv")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_read_csv_empty_file(self, mock_file):
        result = IOUtil.read_csv("empty.csv")
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open, read_data="name,age\nAlice,30\nBob,25.5\nCharlie")
    def test_read_csv_inconsistent_columns(self, mock_file):
        result = IOUtil.read_csv("inconsistent.csv")
        self.assertEqual(len(result), 3)
        self.assertIn('Charlie', result[-1].values())

    # Additional test for different data types
    @patch("builtins.open", new_callable=mock_open, read_data="name,age,score\nAlice,30,85.5\nBob,25,90")
    def test_read_csv_varied_data_types(self, mock_file):
        expected_output = [{'name': 'Alice', 'age': '30', 'score': '85.5'}, {'name': 'Bob', 'age': '25', 'score': '90'}]
        result = IOUtil.read_csv("varied_types.csv")
        self.assertEqual(result, expected_output)

    @patch("builtins.open", new_callable=mock_open,
           read_data='{"name": "Alice", "age": 30}\n{"name": "Bob", "age": 25}\n')
    def test_read_jsonl_valid_file(self, mock_file):
        result = IOUtil.read_jsonl("dummy.jsonl")
        self.assertEqual(result, self.expected_valid_output)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_read_jsonl_nonexistent_file(self, mock_file):
        with self.assertRaises(FileNotFoundError):
            IOUtil.read_jsonl("nonexistent.jsonl")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_read_jsonl_empty_file(self, mock_file):
        result = IOUtil.read_jsonl("empty.jsonl")
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "Alice", "age": 30}\n{"name": "Bob"}\n')
    def test_read_jsonl_mixed_data_types(self, mock_file):
        expected_output = [{'name': 'Alice', 'age': 30}, {'name': 'Bob'}]
        result = IOUtil.read_jsonl("mixed_types.jsonl")
        self.assertEqual(result, expected_output)

    @patch("builtins.open", new_callable=mock_open,
           read_data='{"name": "Alice", "age": 30}\nInvalid JSON\n{"name": "Bob", "age": 25}\n')
    def test_read_jsonl_invalid_json_format(self, mock_file):
        with self.assertRaises(json.JSONDecodeError):
            IOUtil.read_jsonl("invalid.jsonl")

    def test_write_json_valid_data(self):
        mock_file = NonClosingStringIO()
        with patch("builtins.open", return_value=mock_file):
            IOUtil.write_json(self.valid_data, "test.json")
            # Since close is overridden, the file remains open
            mock_file.seek(0)
            written_data = mock_file.getvalue()
            expected_json = json.dumps(self.valid_data, indent=4)
            self.assertEqual(written_data, expected_json)

    def test_write_json_empty_list(self):
        with patch("builtins.open", mock_open()) as mocked_file:
            IOUtil.write_json(self.empty_data, "test.json")
            mocked_file.assert_called_once_with("test.json", 'w')
            mocked_file().write.assert_called_once_with(json.dumps(self.empty_data, indent=4))

    def test_write_json_non_serializable_data(self):
        non_serializable_data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': lambda x: x}]
        with self.assertRaises(TypeError):
            IOUtil.write_json(non_serializable_data, "test.json")

    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "Alice", "age": 30}')
    def test_read_json_valid_file(self, mock_file):
        expected_output = {"name": "Alice", "age": 30}
        result = IOUtil.read_json("valid.json")
        self.assertEqual(result, expected_output)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_read_json_nonexistent_file(self, mock_file):
        with self.assertRaises(FileNotFoundError):
            IOUtil.read_json("nonexistent.json")

    @patch("builtins.open", new_callable=mock_open, read_data='{name: Alice, age: 30}')
    def test_read_json_invalid_format(self, mock_file):
        with self.assertRaises(json.JSONDecodeError):
            IOUtil.read_json("invalid.json")

    def open_mock(self, file, mode='r', newline=None):
        mock_files = {
            'file1.csv': mock_open(read_data=self.csv_data1).return_value,
            'file2.csv': mock_open(read_data=self.csv_data2).return_value,
            'empty1.csv': mock_open(read_data=self.empty_data).return_value,
            'empty2.csv': mock_open(read_data=self.empty_data).return_value
        }
        return mock_files.get(file, mock_open().return_value)

    def test_merge_csv_files_valid(self):
        with patch("builtins.open", side_effect=self.open_mock):
            IOUtil.merge_csv_files(['file1.csv', 'file2.csv'], 'merged.csv')
            # Additional assertions can be added to validate the content of the merged file.

    def test_merge_csv_files_nonexistent(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                IOUtil.merge_csv_files(['nonexistent.csv'], 'output.csv')

    def test_merge_csv_files_different_columns(self):
        with patch("builtins.open", side_effect=self.open_mock):
            IOUtil.merge_csv_files(['file1.csv', 'file2.csv'], 'merged_diff_cols.csv')
            # Additional assertions can be added to validate the content of the merged file.

    def test_merge_csv_files_empty_files(self):
        with patch("builtins.open", side_effect=self.open_mock):
            IOUtil.merge_csv_files(['empty1.csv', 'empty2.csv'], 'merged_empty.csv')
            # Assert that the output file is created and is empty

    def test_to_csv_valid_data(self):
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            IOUtil.to_csv(self.valid_data, "test.csv")

        # Aggregate all calls to write and concatenate their arguments
        write_calls = mock_file().write.call_args_list
        written_data = ''.join(call_arg[0][0] for call_arg in write_calls)

        # Normalize line endings to Unix style for comparison
        written_data_normalized = written_data.replace('\r\n', '\n')
        self.assertEqual(written_data_normalized, self.expected_csv)

    @patch("os.path.exists", return_value=False)
    def test_to_csv_nonexistent_dir_file_exist_ok_false(self, mock_exists):
        with self.assertRaises(FileNotFoundError):
            IOUtil.to_csv(self.valid_data, "nonexistent_dir/test.csv", file_exist_ok=False)

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_to_csv_nonexistent_dir_file_exist_ok_true(self, mock_exists, mock_makedirs):
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            IOUtil.to_csv(self.valid_data, "nonexistent_dir/test.csv", file_exist_ok=True)
            mock_makedirs.assert_called_once_with(os.path.dirname("nonexistent_dir/test.csv"), exist_ok=True)

    def test_to_csv_empty_list(self):
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            IOUtil.to_csv([], "empty.csv")

        # Assert that open was never called, as the method should return early for an empty list
        mock_file.assert_not_called()

    def test_append_to_jsonl_valid_data(self):
        mock_file = mock_open()
        data = {'name': 'Alice', 'age': 30}
        with patch("builtins.open", mock_file, create=True):
            IOUtil.append_to_jsonl(data, "test.jsonl")
            mock_file().write.assert_called_once_with(json.dumps(data) + "\n")

    def test_append_to_jsonl_new_file(self):
        mock_file = mock_open()
        data = {'name': 'Bob', 'age': 25}
        with patch("builtins.open", mock_file, create=True):
            IOUtil.append_to_jsonl(data, "new_file.jsonl")
            mock_file.assert_called_once_with("new_file.jsonl", "a")
            mock_file().write.assert_called_once_with(json.dumps(data) + "\n")

    def test_append_to_jsonl_non_serializable_data(self):
        class NonSerializable:
            pass

        non_serializable_data = NonSerializable()
        with self.assertRaises(TypeError):
            IOUtil.append_to_jsonl(non_serializable_data, "test.jsonl")

    def test_to_temp_with_valid_string(self):
        test_input = "Test String"
        temp_file = IOUtil.to_temp(test_input)
        with open(temp_file.name, 'r') as file:
            content = json.load(file)
            self.assertEqual(content, [test_input])
        os.remove(temp_file.name)  # Clean up the temporary file

    def test_to_temp_with_valid_iterable(self):
        test_input = ["Test", "String"]
        temp_file = IOUtil.to_temp(test_input)
        with open(temp_file.name, 'r') as file:
            content = json.load(file)
            self.assertEqual(content, test_input)
        os.remove(temp_file.name)  # Clean up the temporary file

    def test_to_temp_with_non_serializable_data(self):
        class NonSerializable:
            pass

        non_serializable_data = NonSerializable()
        with self.assertRaises(TypeError):
            IOUtil.to_temp(non_serializable_data)
            

if __name__ == '__main__':
    unittest.main()
