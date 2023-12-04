from collections import deque
from .sys_util import to_csv, create_path


class DataLogger:
    """
    Logs data entries and outputs them to a CSV file.
    
    This class provides a logging mechanism for data entries that can be saved to a
    CSV file. It offers methods for appending new log entries, saving the log to a CSV file,
    and setting the directory where the logs should be saved.

    Attributes:
        dir (str): The directory where the log files are to be saved.
        log (deque): A deque that stores log entries.

    Methods:
        __call__(entry): Appends a new entry to the log.
        to_csv(dir: str, filename: str, verbose: bool, timestamp: bool, dir_exist_ok: bool, file_exist_ok: bool): 
            Converts the log to a CSV format and saves it to a file.
        set_dir(dir: str): Sets the directory for saving log files.
    """

    def __init__(self, dir= None, log: list = None) -> None:
        """
        Initializes a new instance of the DataLogger class.

        Parameters:
            dir (str, optional): The directory where the log files will be saved. Defaults to None.
            log (list, optional): An initial list of log entries. Defaults to an empty deque.
        """
        self.dir = dir
        self.log = deque(log) if log else deque()

    def __call__(self, entry):
        """
        Appends a new entry to the log.

        Parameters:
            entry: The entry to append to the log. The entry can be of any datatype.
        """
        self.log.append(entry)

    def to_csv(self, dir: str, filename: str, verbose: bool = True, timestamp: bool = True, dir_exist_ok=True, file_exist_ok=False):
        """
        Converts the log to a CSV format and saves it to a file.

        Parameters:
            dir (str): The directory where the CSV file will be saved.
            filename (str): The name of the CSV file.
            verbose (bool, optional): If True, prints a message after saving the log. Defaults to True.
            timestamp (bool, optional): If True, appends a timestamp to the filename. Defaults to True.
            dir_exist_ok (bool, optional): If True, overrides the existing directory if needed. Defaults to True.
            file_exist_ok (bool, optional): If True, overrides the existing file if needed. Defaults to False.

        Postconditions:
            Saves the log entries to a CSV file and clears the `log` attribute.
            Optionally prints a message with the number of log entries saved and the file path.
        """
        filepath = create_path(dir=dir, filename=filename, timestamp=timestamp, dir_exist_ok=dir_exist_ok)
        to_csv(list(self.log), filepath, file_exist_ok=file_exist_ok)
        n_logs = len(list(self.log))
        self.log = deque()
        if verbose:
            print(f"{n_logs} logs saved to {filepath}")
            
    def set_dir(self, dir: str):
        """
        Sets the directory where log files will be saved.

        Parameters:
            dir (str): The directory to set for saving log files.
        """
        self.dir = dir
        