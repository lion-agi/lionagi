import os
import hashlib
from datetime import datetime
from collections import deque

from .sys_util import to_csv


class DataLogger:
    """
    Class for logging data with support for unique IDs, timestamps, and CSV export.

    This class provides a simple data logging mechanism where each entry is assigned
    a unique ID based on the current time and random bytes. It supports storing logs in
    a specified directory, with options for including timestamps and exporting to CSV.

     Attributes:
        dir_ (Optional[str]): The directory path where logs will be stored.
        log (deque): A deque to hold log entries.

    Methods:
        _generate_id: Generates a unique ID based on the current time and random bytes.
        _get_timestamp: Gets the current timestamp in a specific format.
        _filepath: Generates a file path based on the directory, filename, and timestamp option.
        __call__: Appends a log entry to the internal log deque.
        to_csv: Exports the log entries to a CSV file.
    """
    def __init__(self, dir_= None, log: list = None) -> None:
        """
        Initializes a DataLogger object with a specified directory and log entries.

        Args:
            dir_: The directory path where logs will be stored.
            log (List): The initial log entries, if provided.

        Example:
            >>> logger = DataLogger(dir_='logs', log=['entry1', 'entry2'])
        """
        self.dir_ = dir_
        self.log = deque(log) if log else deque()

    @staticmethod
    def _generate_id() -> str:
        """
        Generates a unique ID based on the current time and random bytes.

        Returns:
            str: A unique ID.
        """
        current_time = datetime.now().isoformat().encode('utf-8')
        random_bytes = os.urandom(16)
        return hashlib.sha256(current_time + random_bytes).hexdigest()[:16]
    
    @staticmethod
    def _get_timestamp() -> str:
        """
        Gets the current timestamp in a specific format.

        Returns:
            str: Current timestamp.
        """
        return datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")

    @staticmethod
    def _filepath(dir_: str, filename: str, timestamp: bool = True) -> str:
        """
        Generates a file path based on the directory, filename, and timestamp option.

        Args:
            dir_ (str): The directory path.
            filename (str): The name of the file.
            timestamp (bool): Whether to include a timestamp in the file name.

        Return:
            str: The generated file path.

        Example:
            >>> file_path = DataLogger._filepath(dir_='logs/', filename='logfile.txt', timestamp=True)
        """
        os.makedirs(dir_, exist_ok=True)
        if timestamp:
            timestamp = DataLogger._get_timestamp()
            return f"{dir_}{timestamp}{filename}"
        else:
            return f"{dir_}{filename}"

    def __call__(self, entry):
        """
        Appends a log entry to the internal log deque.

        Args:
            entry: The log entry to be appended.
        """
        self.log.append(entry)

    def to_csv(self, dir_: str, filename: str, verbose: bool, timestamp: bool):
        """
        Exports the log entries to a CSV file.

        Args:
            dir_ (str): The directory path for exporting the CSV file.
            filename (str): The name of the CSV file.
            verbose (bool): Whether to print a verbose message after export.
            timestamp (bool): Whether to include a timestamp in the exported file name.

        Example:
            >>> logger.to_csv(dir_='exports/', filename='exported_logs.csv', verbose=True, timestamp=True)
        """
        filepath = self._filepath(dir_=dir_, filename=filename, timestamp=timestamp)
        log_list = list(self.log)
        to_csv(log_list, filepath)
        n_logs = len(log_list)
        self.log = deque()
        if verbose:
            print(f"{n_logs} logs saved to {filepath}")
            