from collections import deque
from typing import Dict, Any
from ..utils.sys_util import get_timestamp, create_path, as_dict
from ..utils.io_util import IOUtil


class DataLogger:
    """
    A class for logging data entries and exporting them as CSV files.

    This class provides functionality to log data entries in a deque and 
    supports exporting the logged data to a CSV file. The DataLogger can 
    be configured to use a specific directory for saving files.

    Attributes:
        dir (Optional[str]): 
            The default directory where CSV files will be saved.
        log (deque): 
            A deque object that stores the logged data entries.

    Methods:
        __call__:
            Adds an entry to the log.
        to_csv:
            Exports the logged data to a CSV file and clears the log.
        set_dir:
            Sets the default directory for saving CSV files.
    """    

    def __init__(self, dir= None, log: list = None) -> None:
        """
        Initializes the DataLogger with an optional directory and initial log.

        Parameters:
            dir (Optional[str]): The directory where CSV files will be saved. Defaults to None.

            log (Optional[List]): An initial list of log entries. Defaults to an empty list.
        """        
        self.dir = dir
        self.log = deque(log) if log else deque()

    def add_entry(self, entry: Dict[str, Any], level: str = "INFO") -> None:
        """
        Adds a new entry to the log with a timestamp and a log level.

        Args:
            entry (Dict[str, Any]): The data entry to be added to the log.
            level (str): The log level for the entry (e.g., "INFO", "ERROR"). Defaults to "INFO".
        """
        self.log.append({
            "timestamp": get_timestamp(), "level": level, **as_dict(entry)
        })
        
    def set_dir(self, dir: str) -> None:
        """
        Sets the default directory for saving CSV files.

        Parameters:
            dir (str): The directory to be set as the default for saving files.
        """
        self.dir = dir

    def to_csv(
        self, filename: str, 
        file_exist_ok: bool = False,  
        timestamp = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear = True
    ) -> None:
        """
        Exports the logged data to a CSV file, using the provided utilities for path creation and timestamping.

        Args:
            filename (str): The name of the CSV file.
            file_exist_ok (bool): If True, creates the directory for the file if it does not exist. Defaults to False.
            verbose (bool): If True, prints a message upon completion. Defaults to True.
            time_prefix (bool): If True, adds the timestamp as a prefix to the filename. Defaults to False.
        """
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = create_path(
            self.dir, filename, timestamp=timestamp, 
            dir_exist_ok=file_exist_ok, time_prefix=time_prefix
        )
        IOUtil.to_csv(list(self.log), filepath)

        if verbose:
            print(f"{len(self.log)} logs saved to {filepath}")

        if clear:
            self.log.clear()

    def to_jsonl(
        self, filename: str, 
        timestamp = False, 
        time_prefix=False,
        file_exist_ok: bool = False, 
        verbose: bool = True, 
        clear = True
    ) -> None:
        """
        Exports the logged data to a JSONL file and optionally clears the log.

        Parameters:
            filename (str): The name of the JSONL file.
            file_exist_ok (bool): If True, creates the directory for the file if it does not exist. Defaults to False.
            verbose (bool): If True, prints a message upon completion. Defaults to True.
        """
        if not filename.endswith('.jsonl'):
            filename += '.jsonl'

        filepath = create_path(
            self.dir, filename, timestamp=timestamp, 
            dir_exist_ok=file_exist_ok, time_prefix=time_prefix
        )
        
        for entry in self.log:
            IOUtil.append_to_jsonl(entry, filepath)

        if verbose:
            print(f"{len(self.log)} logs saved to {filepath}")

        if clear:
            self.log.clear()
