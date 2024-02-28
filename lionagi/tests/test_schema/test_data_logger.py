from lionagi.core.schema.data_logger import *
import unittest
from unittest.mock import patch, mock_open
import shutil


class TestDLog(unittest.TestCase):

    def test_dlog_initialization_and_access(self):
        """Test initialization and attribute access of the DLog class."""
        input_sample = {"key": "value"}
        output_sample = ["list", "of", "values"]

        log_entry = DLog(input_data=input_sample, output_data=output_sample)

        self.assertEqual(log_entry.input_data, input_sample)
        self.assertEqual(log_entry.output_data, output_sample)

    # def test_dlog_serialization_includes_timestamp(self):
    #     """Test serialization includes a dynamically generated timestamp."""
    #     input_sample = "input data"
    #     output_sample = "output data"
    #     fake_timestamp = "2023-01-01T00:00:00"

    #     with patch('lionagi.util.SysUtil.get_timestamp', return_value=fake_timestamp):
    #         log_entry = DLog(input_data=input_sample, output_data=output_sample)
    #         serialized_log = log_entry.serialize()

    #         self.assertEqual(serialized_log['input_data'], input_sample)
    #         self.assertEqual(serialized_log['output_data'], output_sample)
    #         self.assertEqual(serialized_log['timestamp'], fake_timestamp)


class TestDataLogger(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path('data/')

    def tearDown(self):
        if self.data_dir.exists():
            shutil.rmtree(self.data_dir)

    def test_initialization_and_configuration(self):
        """Test DataLogger initialization with various configurations."""
        default_logger = DataLogger()
        self.assertEqual(len(default_logger.log), 0)
        self.assertEqual(default_logger.filename, 'log')

        custom_logger = DataLogger(persist_path='/custom/path', filename='custom_log')
        self.assertEqual(custom_logger.persist_path, Path('/custom/path'))
        self.assertEqual(custom_logger.filename, 'custom_log')

    def test_log_entry_management(self):
        """Test appending new log entries."""
        logger = DataLogger()
        logger.append(input_data="test input", output_data="test output")
        self.assertEqual(len(logger.log), 1)
        logger.to_csv_file(filename='test.csv', clear=True, dir_exist_ok=True)

    @patch('pandas.DataFrame.to_csv')
    def test_to_csv_exporting(self, mock_to_csv):
        """Test exporting logs to CSV."""
        logger = DataLogger()
        logger.append(input_data="input", output_data="output")
        logger.to_csv_file(filename='test.csv', clear=True, dir_exist_ok=True)

        mock_to_csv.assert_called_once()
        self.assertEqual(len(logger.log), 0)  # Assuming clear=True

    @patch('pandas.DataFrame.to_json')
    def test_to_json_exporting(self, mock_to_json):
        """Test exporting logs to JSON."""
        logger = DataLogger()
        logger.append(input_data="input", output_data="output")
        logger.to_json_file(filename='test.json', clear=True)

        mock_to_json.assert_called_once()
        self.assertEqual(len(logger.log), 0)  # Assuming clear=True

    @patch('atexit.register')
    def test_save_at_exit_registration(self, mock_register):
        """Test that save_at_exit is registered at initialization."""
        DataLogger()
        mock_register.assert_called()


if __name__ == '__main__':
    unittest.main()
