from collections import deque
from typing import List, Optional
from ..utils.sys_util import create_path
from ..utils.io_util import to_csv


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
            dir (Optional[str]): 
                The directory where CSV files will be saved. Defaults to None.
            log (Optional[List]): 
                An initial list of log entries. Defaults to an empty list.
        """        
        self.dir = dir
        self.log = deque(log) if log else deque()

    def __call__(self, entry):
        """
        Adds a new entry to the log.

        Parameters:
            entry: 
                The data entry to be added to the log.
        """        
        self.log.append(entry)

    def to_csv(self, filename: str, dir: Optional[str] = None, verbose: bool = True, 
               timestamp: bool = True, dir_exist_ok: bool = True, file_exist_ok: bool = False) -> None:
        """
        Exports the logged data to a CSV file and optionally clears the log.

        Parameters:
            filename (str): 
                The name of the CSV file.
            dir (Optional[str]): 
                The directory to save the file. Defaults to the instance's dir attribute.
            verbose (bool): 
                If True, prints a message upon completion. Defaults to True.
            timestamp (bool): 
                If True, appends a timestamp to the filename. Defaults to True.
            dir_exist_ok (bool): 
                If True, will not raise an error if the directory already exists. Defaults to True.
            file_exist_ok (bool): 
                If True, overwrites the file if it exists. Defaults to False.

        Side Effects:
            Clears the log after saving the CSV file.
            Prints a message indicating the save location and number of logs saved if verbose is True.
        """        
        dir = dir or self.dir
        filepath = create_path(
            dir=dir, filename=filename, timestamp=timestamp, dir_exist_ok=dir_exist_ok)
        to_csv(list(self.log), filepath, file_exist_ok=file_exist_ok)
        n_logs = len(list(self.log))
        self.log = deque()
        if verbose:
            print(f"{n_logs} logs saved to {filepath}")
            
    def set_dir(self, dir: str) -> None:
        """
        Sets the default directory for saving CSV files.

        Parameters:
            dir (str): 
                The directory to be set as the default for saving files.
        """
        self.dir = dir
        