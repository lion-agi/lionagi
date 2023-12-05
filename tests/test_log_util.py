import unittest
from lionagi.utils.log_util import DataLogger
from unittest.mock import patch
import os
import csv
import tempfile

class TestDataLogger(unittest.TestCase):
    """
    Unit tests for the DataLogger class.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the temporary directory after each test
        os.rmdir(self.temp_dir)

    def test_init(self):
        logger = DataLogger(dir='test_dir', log=[1, 2, 3])
        self.assertEqual(logger.dir, 'test_dir')
        self.assertListEqual(list(logger.log), [1, 2, 3])

    def test_call(self):
        logger = DataLogger()
        logger('new entry')
        self.assertListEqual(list(logger.log), ['new entry'])

    def test_to_csv(self):
        logger = DataLogger(dir=self.temp_dir, log=[{'id': 1, 'value': 10}, {'id': 2, 'value':20}])

        with patch('builtins.print') as mock_print:
            logger.to_csv(dir=self.temp_dir, filename='test.csv', timestamp=False)

        csv_filepath = self.temp_dir+'test.csv'
        mock_print.assert_called_with(f"2 logs saved to {csv_filepath}")

        self.assertTrue(os.path.exists(csv_filepath))

        with open(csv_filepath, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            rows = list(csv_reader)
            self.assertEqual(len(rows), 3)
            self.assertListEqual(rows[0], ['id', 'value'])
            self.assertListEqual(rows[1], ['1', '10'])
            self.assertListEqual(rows[2], ['2', '20'])

        self.assertListEqual(list(logger.log), [])

    def test_set_dir(self):
        logger = DataLogger()
        logger.set_dir('new_test_dir')
        self.assertEqual(logger.dir, 'new_test_dir')

if __name__ == '__main__':
    unittest.main()
