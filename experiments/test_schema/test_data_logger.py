import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime
from lionagi.core.generic.data_logger import DataLogger, DLog


class TestDataLogger(unittest.TestCase):
    def setUp(self):
        self.logger = DataLogger()

    def test_init_default(self):
        logger = DataLogger()
        self.assertEqual(logger.persist_path, Path("data/logs/"))
        self.assertEqual(logger.filename, "log")

    def test_init_custom(self):
        logger = DataLogger(persist_path="custom_logs", filename="custom_log")
        self.assertEqual(logger.persist_path, Path("custom_logs"))
        self.assertEqual(logger.filename, "custom_log")

    def test_extend_empty(self):
        self.logger.extend([])
        self.assertEqual(len(self.logger.log), 0)

    def test_extend_single(self):
        log = DLog(input_data="input", output_data="output")
        self.logger.extend([log])
        self.assertEqual(len(self.logger.log), 1)
        self.assertEqual(self.logger.log[0], log)

    def test_extend_multiple(self):
        logs = [
            DLog(input_data="input1", output_data="output1"),
            DLog(input_data="input2", output_data="output2"),
        ]
        self.logger.extend(logs)
        self.assertEqual(len(self.logger.log), 2)
        self.assertEqual(self.logger.log[0].input_data, "input1")
        self.assertEqual(self.logger.log[1].output_data, "output2")

    def test_append(self):
        self.logger.append(input_data="input", output_data="output")
        self.assertEqual(len(self.logger.log), 1)
        self.assertEqual(self.logger.log[0].input_data, "input")
        self.assertEqual(self.logger.log[0].output_data, "output")

    @patch("data_logger.SysUtil.create_path")
    @patch("data_logger.convert.to_df")
    def test_to_csv_file_default(self, mock_to_df, mock_create_path):
        mock_create_path.return_value = "test_path.csv"
        mock_df = MagicMock()
        mock_to_df.return_value = mock_df

        self.logger.append(input_data="input", output_data="output")
        self.logger.to_csv_file()

        mock_create_path.assert_called_once()
        mock_to_df.assert_called_once()
        mock_df.to_csv.assert_called_once_with("test_path.csv", index=False)
        self.assertEqual(len(self.logger.log), 0)

    # @patch("data_logger.SysUtil.create_path")
    # @patch("data_logger.convert.to_df")
    # def test_to_csv_file_custom(self, mock_to_df, mock_create_path):
    #     mock_create_path.return_value = "custom_path.csv"
    #     mock_df = MagicMock()
    #     mock_to_df.return_value = mock_df

    #     self.logger.append(input_data="input", output_data="output")
    #     self.logger.to_csv_file(
    #         filename="custom.csv",
    #         dir_exist_ok=False,
    #         timestamp=False,
    #         time_prefix=True,
    #         verbose=False,
    #         clear=False,
    #         flatten_=False,
    #         sep="[^_^]",
    #         index=True,
    #         random_hash_digits=3,
    #     )

    #     mock_create_path.assert_called_once_with(
    #         self.logger.persist_path,
    #         "custom.csv",
    #         timestamp=False,
    #         dir_exist_ok=False,
    #         time_prefix=True,
    #     )
    #     mock_to_df.assert_called_once()
    #     mock_df.to_csv.assert_called_once_with("custom_path.csv", index=True)
    #     self.assertEqual(len(self.logger.log), 1)

    @patch("data_logger.SysUtil.create_path")
    @patch("data_logger.convert.to_df")
    def test_to_json_file_default(self, mock_to_df, mock_create_path):
        mock_create_path.return_value = "test_path.json"
        mock_df = MagicMock()
        mock_to_df.return_value = mock_df

        self.logger.append(input_data="input", output_data="output")
        self.logger.to_json_file()

        mock_create_path.assert_called_once()
        mock_to_df.assert_called_once()
        mock_df.to_json.assert_called_once_with("test_path.json", index=False)
        self.assertEqual(len(self.logger.log), 0)

    # @patch("data_logger.SysUtil.create_path")
    # @patch("data_logger.convert.to_df")
    # def test_to_json_file_custom(self, mock_to_df, mock_create_path):
    #     mock_create_path.return_value = "custom_path.json"
    #     mock_df = MagicMock()
    #     mock_to_df.return_value = mock_df

    #     self.logger.append(input_data="input", output_data="output")
    #     self.logger.to_json_file(
    #         filename="custom.json",
    #         dir_exist_ok=False,
    #         timestamp=False,
    #         time_prefix=True,
    #         verbose=False,
    #         clear=False,
    #         flatten_=False,
    #         sep="[^_^]",
    #         index=True,
    #         random_hash_digits=3,
    #     )

    #     mock_create_path.assert_called_once_with(
    #         self.logger.persist_path,
    #         "custom.json",
    #         timestamp=False,
    #         dir_exist_ok=False,
    #         time_prefix=True,
    #     )
    #     mock_to_df.assert_called_once()
    #     mock_df.to_json.assert_called_once_with("custom_path.json", index=True)
    #     self.assertEqual(len(self.logger.log), 1)

    @patch("data_logger.DataLogger.to_csv_file")
    def test_save_at_exit(self, mock_to_csv_file):
        self.logger.append(input_data="input", output_data="output")
        self.logger.save_at_exit()
        mock_to_csv_file.assert_called_once_with("unsaved_logs.csv", clear=False)


class TestDLog(unittest.TestCase):
    def test_serialize_default(self):
        log = DLog(
            input_data={"key1": "value1", "key2": {"nested": "value"}},
            output_data="output",
        )
        serialized = log.serialize()
        self.assertEqual(
            serialized["input_data"], '{"key1": "value1", "key2[^_^]nested": "value"}'
        )
        self.assertEqual(serialized["output_data"], "output")
        self.assertIsInstance(serialized["timestamp"], str)

    def test_serialize_flatten_false(self):
        log = DLog(
            input_data={"key1": "value1", "key2": {"nested": "value"}},
            output_data="output",
        )
        serialized = log.serialize(flatten_=False)
        self.assertEqual(
            serialized["input_data"], '{"key1": "value1", "key2": {"nested": "value"}}'
        )
        self.assertEqual(serialized["output_data"], "output")
        self.assertIsInstance(serialized["timestamp"], str)

    def test_serialize_custom_sep(self):
        log = DLog(
            input_data={"key1": "value1", "key2": {"nested": "value"}},
            output_data="output",
        )
        serialized = log.serialize(sep=".")
        self.assertEqual(
            serialized["input_data"], '{"key1": "value1", "key2.nested": "value"}'
        )
        self.assertEqual(serialized["output_data"], "output")
        self.assertIsInstance(serialized["timestamp"], str)

    def test_deserialize_default(self):
        input_str = '{"key1": "value1", "key2[^_^]nested": "value"}'
        output_str = "output"
        log = DLog.deserialize(input_str=input_str, output_str=output_str)
        self.assertEqual(
            log.input_data, {"key1": "value1", "key2": {"nested": "value"}}
        )
        self.assertEqual(log.output_data, "output")

    def test_deserialize_unflatten_false(self):
        input_str = '{"key1": "value1", "key2[^_^]nested": "value"}'
        output_str = "output"
        log = DLog.deserialize(
            input_str=input_str, output_str=output_str, unflatten_=False
        )
        self.assertEqual(
            log.input_data, '{"key1": "value1", "key2[^_^]nested": "value"}'
        )
        self.assertEqual(log.output_data, "output")

    def test_deserialize_custom_sep(self):
        input_str = '{"key1": "value1", "key2.nested": "value"}'
        output_str = "output"
        log = DLog.deserialize(input_str=input_str, output_str=output_str, sep=".")
        self.assertEqual(
            log.input_data, {"key1": "value1", "key2": {"nested": "value"}}
        )
        self.assertEqual(log.output_data, "output")


if __name__ == "__main__":
    unittest.main()
