import csv
import json
import os
from collections import deque
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional, Deque


class DataLogger:
    """A class for logging data entries and saving them to a CSV or JSON file.

    Attributes:
        dir (Optional[str]): The directory where log files will be saved.
        log (Deque[Dict[str, Any]]): A deque that stores log entries with a maximum size.
        buffer_limit (int): The maximum number of entries the log can hold.
        auto_flush_size (int): The number of entries to reach before auto-flushing the log.
        lock (Lock): A threading lock to ensure thread safety.

    Examples:
        >>> logger = EnhancedDataLogger(dir="logs", auto_flush_size=10)
        >>> logger({"event": "start", "value": 1}, level="INFO")
        >>> logger({"event": "stop", "value": 0}, level="ERROR")
        >>> logger.flush(filename="event_log", to_json=False)

        This will create a CSV file 'event_log.csv' in the 'logs' directory with two log entries.

        >>> logger = EnhancedDataLogger(dir="logs", auto_flush_size=10)
        >>> logger({"event": "start", "value": 1}, level="INFO")
        >>> logger({"event": "update", "value": 5}, level="DEBUG")
        >>> logger.flush(filename="event_log", to_json=True)

        This will create a JSON file 'event_log.jsonl' in the 'logs' directory with two log entries.
    """

    def __init__(self, dir: Optional[str] = None, log: Optional[List[Dict[str, Any]]] = None, buffer_limit: int = 1000, auto_flush_size: int = 100) -> None:
        self.dir = dir
        self.log: Deque[Dict[str, Any]] = deque(log, maxlen=buffer_limit) if log else deque(maxlen=buffer_limit)
        self.buffer_limit = buffer_limit
        self.auto_flush_size = auto_flush_size
        self.lock = Lock()

    def __call__(self, entry: Dict[str, Any], level: str = "INFO") -> None:
        """Add a log entry to the log deque with a specified log level.

        Args:
            entry (Dict[str, Any]): The log entry to be added.
            level (str): The log level for the entry (e.g., "INFO", "ERROR").
        """
        with self.lock:
            self.log.append({"timestamp": self.get_timestamp(), "level": level, **entry})

    def flush(self, filename: str = "log", to_json: bool = False) -> None:
        """Flush the log entries to a file in either CSV or JSON format.

        Args:
            filename (str): The base name of the file to write the logs to.
            to_json (bool): If True, logs are written in JSON format; otherwise, in CSV format.
        """
        if not self.log:
            return
        dir = self.dir or "."
        filepath = self.create_path(dir=dir, filename=filename, to_json=to_json)
        num_entries = len(self.log)
        if to_json:
            self.to_json(filepath)
        else:
            self.to_csv(filepath)
        self.log.clear()
        print(f"Flushed {num_entries} entries to {'JSON' if to_json else 'CSV'} file.")

    def to_csv(self, filepath: str) -> None:
        """Write the log entries to a CSV file.

        Args:
            filepath (str): The full path to the CSV file.
        """
        num_entries = len(self.log)
        with open(filepath, 'a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.log[0].keys())
            if os.stat(filepath).st_size == 0:  # Write header only if file is empty
                writer.writeheader()
            writer.writerows(self.log)
        print(f"Wrote {num_entries} entries to CSV file.")

    def to_json(self, filepath: str) -> None:
        """Write the log entries to a JSON file.

        Args:
            filepath (str): The full path to the JSON file.
        """
        num_entries = len(self.log)
        with open(filepath, 'a') as json_file:
            for entry in self.log:
                json_file.write(json.dumps(entry) + "\n")
        print(f"Wrote {num_entries} entries to JSON file.")

    def create_path(self, dir: str, filename: str, to_json: bool = False) -> str:
        """Create the full file path for the log file, ensuring the directory exists.

        Args:
            dir (str): The directory where the file will be created.
            filename (str): The base name of the file.
            to_json (bool): If True, the file extension will be '.jsonl'; otherwise, '.csv'.

        Returns:
            str: The full file path for the log file.
        """
        ext = "jsonl" if to_json else "csv"
        filepath = f"{dir}/{filename}.{ext}"
        os.makedirs(dir, exist_ok=True)
        return filepath

    def get_timestamp(self) -> str:
        """Get the current timestamp in 'YYYYMMDDHHMMSS' format.

        Returns:
            str: The current timestamp.
        """
        return datetime.now().strftime("%Y%m%d%H%M%S")
    