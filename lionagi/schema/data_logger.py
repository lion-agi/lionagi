import atexit
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Any, Union, List
from pathlib import Path

from lionagi.utils import get_timestamp, create_path, to_df


@dataclass
class DLog:
    """
    Represents a log entry with input, output, and a timestamp, facilitating structured logging.

    Attributes:
        input_data (Any): Input data for the log entry.
        output_data (Any): Output data for the log entry.
        timestamp (str): Timestamp for when the log entry was created. Defaulted to the current time.
    """
    __slots__ = ['input_data', 'output_data', 'timestamp']
    input_data: Any
    output_data: Any
    timestamp: str = field(default_factory=get_timestamp)

class DataLogger:
    """
    Manages and persists logging of input-output data pairs, offering support for CSV and JSON export formats.

    This class accumulates log entries and provides functionalities for exporting these logs to disk.
    It is capable of handling directory creation, supports timestamping for file naming, and is designed
    with proxy path compatibility for flexible file saving locations.

    Attributes:
        persist_path (Path): Directory path where log files will be saved. Defaults to 'data/logs/'.
        log (Deque[Dict]): Container for storing log entries in a structured dictionary format.
        filename (str): Base filename used when saving logs, with extensions added based on format.

    Examples:
        Initializing DataLogger with a custom directory and filename:
        >>> logger = DataLogger(persist_path='path/to/logs', filename='my_logs')
        >>> logger.append({'input': 'data1', 'output': 'result1'})
        >>> logger.to_csv('exported_logs.csv')

        Appending log entries and saving them:
        >>> logger.append(input_data="test input", output_data="test output")
        >>> logger.to_json('logs.json', clear=True)
    """

    def __init__(self, persist_path: Optional[Union[str, Path]] = None, log: Optional[List[Dict]] = None, 
                 filename: Optional[str] = None) -> None:
        """
        Initializes a new instance of DataLogger.

        Args:
            persist_path (Optional[Union[str, Path]]): Directory path for saving log files. Accepts either string paths or Path objects.
            log (Optional[List[Dict]]): Initial list of log entries. Each entry should be a dictionary.
            filename (Optional[str]): Base filename for saving logs. Extension is determined by export format.

        """
        self._persist_path = Path(persist_path) if persist_path else Path('data/logs/')
        self.log = deque(log) if log else deque()
        self.filename = filename or 'log'
        atexit.register(self.save_at_exit)

    @property
    def persist_path(self) -> Path:
        """
        Retrieves the current directory path for saving log files.
        """
        return self._persist_path
    
    @persist_path.setter
    def persist_path(self, new_directory: Union[str, Path]):
        """
        Updates the directory path for saving log files.

        Args:
            new_directory (Union[str, Path]): The new directory path for log files.
        """
        self._persist_path = Path(new_directory)

    def append(self, input_data: Any, output_data: Any) -> None:
        """
        Appends a new log entry with specified input and output data to the log deque.

        Args:
            input_data (Any): The input data for the log entry.
            output_data (Any): The output data for the log entry.
        """
        self.log.append(asdict(DLog(input_data=input_data, output_data=output_data)))

    def to_csv(self, filename: str = 'log.csv', file_exist_ok: bool = False,  
               timestamp=True, time_prefix: bool = False, verbose: bool = True,
               clear=True, **kwargs) -> None:
        """
        Exports the log entries to a CSV file within the persist directory, with options for 
        timestamping and file naming. This method leverages pandas DataFrame for CSV conversion, 
        supporting additional pandas `to_csv` method arguments via `**kwargs`.

        Args:
            filename (str): The desired filename for the CSV output. Automatically appends '.csv'
                            if not included. The file is saved within the specified persist directory.
            file_exist_ok (bool): Allows writing to an existing directory without raising an error. 
                                When False, raises an error if the directory exists.
            timestamp (bool): Appends a current timestamp to the filename for uniqueness. The timestamp
                            format is "YYYY-MM-DDTHH_MM_SS", adapted for file naming.
            time_prefix (bool): Determines the positioning of the timestamp in the filename. When 
                                True, the timestamp is prefixed; otherwise, it's suffixed.
            verbose (bool): Enables printing of a message upon successful save, indicating the file 
                            path and the number of logs saved.
            clear (bool): Clears the internal log deque after saving, if True. Useful for freeing 
                        memory or starting fresh after persisting current logs.
            **kwargs: Additional keyword arguments passed directly to the pandas `DataFrame.to_csv` 
                    method, allowing for customization of the CSV output (e.g., index inclusion, 
                    column ordering).

        Raises:
            ValueError: If there's an error during the saving process, encapsulating exceptions 
                        from file writing or DataFrame conversion.

        Examples:
            Saving logs with default settings, resulting in 'log.csv' or a timestamped name in the 
            specified 'data/logs/' directory:
            >>> logger.to_csv()
            # Example save path: 'data/logs/log_2023-10-04T15_30_45.csv'

            Saving logs with a timestamp prefix and specifying a custom filename, without clearing 
            the logs:
            >>> logger.to_csv(filename='detailed_log.csv', time_prefix=True, clear=False)
            # Example save path: 'data/logs/2023-10-04T15_30_45_detailed_log.csv'

            Specifying additional pandas options, such as excluding the index:
            >>> logger.to_csv(filename='no_index_log.csv', index=False)
            # Saves to 'data/logs/no_index_log.csv'
        """

        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = create_path(
            self.persist_path, filename, timestamp=timestamp, 
            dir_exist_ok=file_exist_ok, time_prefix=time_prefix
        )
        try:
            df = to_df(list(self.log))
            df.to_csv(filepath, **kwargs)
            if verbose:
                print(f"{len(self.log)} logs saved to {filepath}")
            if clear:
                self.log.clear()
        except Exception as e:
            raise ValueError(f"Error in saving to csv: {e}")
        
    def to_json(self, filename: str = 'log.json', timestamp=False, time_prefix=False,
                file_exist_ok: bool = False, verbose: bool = True, clear=True, **kwargs) -> None:
        """
        Exports the log entries to a JSON file within the specified persist directory, with options for 
        timestamping and file naming. This method uses pandas DataFrame for JSON conversion, 
        supporting additional pandas `to_json` method arguments via `**kwargs`.

        Args:
            filename (str): The desired filename for the JSON output. Automatically appends '.json'
                            if omitted. The file is saved within the specified persist directory.
            timestamp (bool): Optionally appends a current timestamp to the filename for uniqueness,
                            using the format "YYYY-MM-DDTHH_MM_SS".
            time_prefix (bool): When True, the timestamp is added as a prefix to the filename; 
                                otherwise, as a suffix.
            file_exist_ok (bool): If True, permits writing to an existing directory; raises an error 
                                if the directory exists and this is set to False.
            verbose (bool): If True, prints a confirmation message upon successful save, showing the 
                            file path and the count of logs saved.
            clear (bool): If set to True, clears the log deque after saving, which can be useful for 
                        memory management or logical separation of logged data.
            **kwargs: Passes additional keyword arguments to the pandas `DataFrame.to_json` method, 
                    allowing for detailed control over the JSON output format (e.g., orient, date format).

        Raises:
            ValueError: Encapsulates any exceptions that occur during the file writing or DataFrame 
                        conversion process, providing a clear error message.

        Examples:
            Saving logs to 'log.json' in the specified persist directory with default settings:
            >>> logger.to_json()
            # Example save path: 'data/logs/log.json'

            Saving logs with a custom filename, without appending a timestamp, and specifying 
            additional pandas options:
            >>> logger.to_json(filename='detailed_log.json', orient='records')
            # Saves to 'data/logs/detailed_log.json'
        """

        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = create_path(
            self.persist_path, filename, timestamp=timestamp, 
            dir_exist_ok=file_exist_ok, time_prefix=time_prefix
        )
        
        try:
            df = to_df(list(self.log))
            df.to_json(filepath, **kwargs)
            if verbose:
                print(f"{len(self.log)} logs saved to {filepath}")
            if clear:
                self.log.clear()
        except Exception as e:
            raise ValueError(f"Error in saving to csv: {e}")

    def save_at_exit(self):
        """
        Automatically saves the logs to a CSV file upon program termination.

        This method is registered to execute at program exit, ensuring unsaved logs are persisted.
        """
        if self.log:
            self.to_csv("unsaved_logs.csv", clear=False) 
