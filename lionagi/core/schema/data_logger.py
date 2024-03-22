import atexit
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from lionagi.libs import SysUtil, convert, nested


# TODO: there should be a global data logger, under setting


@dataclass
class DLog:
    """
    Represents a log entry in a structured logging system, encapsulating both the
    input to and output from a data processing operation, along with an automatically
    generated timestamp indicating when the log entry was created.

    The primary use of this class is to provide a standardized format for logging data
    transformations or interactions within an application, facilitating analysis and
    debugging by maintaining a clear record of data states before and after specific
    operations.

    Attributes:
            input_data (Any): The data received by the operation. This attribute can be of
                                              any type, reflecting the flexible nature of input data to
                                              various processes.
            output_data (Any): The data produced by the operation. Similar to `input_data`,
                                               this attribute supports any type, accommodating the diverse
                                               outputs that different operations may generate.

    Methods: serialize: Converts the instance into a dictionary, suitable for
    serialization, and appends a timestamp to this dictionary, reflecting the current
    time.
    """

    input_data: Any
    output_data: Any

    def serialize(self, *, flatten_=True, sep="[^_^]") -> Dict[str, Any]:
        """
        Converts the DLog instance to a dictionary, suitable for serialization. This
        method is particularly useful for exporting log entries to formats like JSON or
        CSV. In addition to the data attributes, it appends a timestamp to the
        dictionary, capturing the exact time the log entry was serialized.

        Returns:
                Dict[str, Any]: A dictionary representation of the DLog instance, including
                                                'input_data', 'output_data', and 'timestamp' keys.
        """
        log_dict = {}

        if flatten_:
            if isinstance(self.input_data, dict):
                log_dict["input_data"] = convert.to_str(
                    nested.flatten(self.input_data, sep=sep)
                )
            if isinstance(self.output_data, dict):
                log_dict["output_data"] = convert.to_str(
                    nested.flatten(self.output_data, sep=sep)
                )

        else:
            log_dict["input_data"] = self.input_data
            log_dict["output_data"] = self.output_data

        log_dict["timestamp"] = SysUtil.get_timestamp()

        return log_dict

    @classmethod
    def deserialize(
        cls, *, input_str, output_str, unflatten_=True, sep="[^_^]"
    ) -> Dict[str, Any]:
        """
        [^_^] is reserved, do not add this in dictionary keys, otherwise the structrue
        won't be reserved

        Converts the DLog instance to a dictionary, suitable for serialization. This
        method is particularly useful for exporting log entries to formats like JSON or
        CSV. In addition to the data attributes, it appends a timestamp to the
        dictionary, capturing the exact time the log entry was serialized.

        Returns:
                Dict[str, Any]: A dictionary representation of the DLog instance, including
                                                'input_data', 'output_data', and 'timestamp' keys.
        """
        input_data = ""
        output_data = ""

        if unflatten_:
            input_data = nested.unflatten(convert.to_dict(input_str), sep=sep)
            output_data = nested.unflatten(convert.to_dict(output_str), sep=sep)

        else:
            input_data = input_str
            output_data = output_str

        return cls(input_data=input_data, output_data=output_data)


class DataLogger:
    """
    Manages the accumulation, structuring, and persistence of log entries pertaining to
    data processing activities within an application. The datalogger is designed to capture
    input-output data pairs across operations, offering functionalities for exporting
    these logs to disk in both CSV and JSON formats.

    The class ensures that log entries are stored in an orderly fashion and can be
    easily retrieved or persisted for analysis, debugging, or record-keeping purposes.
    It supports customizable file naming, directory management, and automatic log saving
    at program exit, among other features.

    Attributes:
            persist_path (Path): The filesystem path to the directory where log files will
                                                     be saved. Defaults to a subdirectory 'data/logs/' within
                                                     the current working directory.
            log (Deque[Dict]): A deque object that acts as the container for log entries.
                                               Each log entry is stored as a dictionary, facilitating easy
                                               conversion to various data formats.
            filename (str): The base name used for log files when saved. The actual filepath
                                            may include a timestamp or other modifiers based on the class's
                                            configuration.

    Methods:
            append: Adds a new log entry to the datalogger.
            to_csv_file: Exports accumulated log entries to a CSV file.
            to_json_file: Exports accumulated log entries to a JSON file.
            save_at_exit: Ensures that unsaved log entries are persisted to a CSV file when
                                      the program terminates.

    Usage Example:
            >>> datalogger = DataLogger(persist_path='my/logs/directory', filepath='process_logs')
            >>> datalogger.append(input_data="Example input", output_data="Example output")
            >>> datalogger.to_csv_file('finalized_logs.csv', clear=True)

    This example demonstrates initializing a `DataLogger` with a custom directory and
    filepath, appending a log entry, and then exporting the log to a CSV file.
    """

    def __init__(
        self,
        persist_path: str | Path | None = None,
        log: List[Dict] | None = None,
        filename: str | None = None,
    ) -> None:
        """
        initializes a DataLogger instance, preparing it for structured logging of data
        processing activities. allows for customization of storage directory, initial
        logs, and base filepath for exports.

        Args:
                persist_path (str | Path | None, optional):
                        The file system path to the directory where log files will be persisted.
                        if not provided, defaults to 'data/logs/' within the current working
                        directory. this path is used for all subsequent log export operations.
                log (list[Dict[str, Any]] | None, optional):
                        An initial collection of log entries to populate the datalogger. each entry
                        should be a dictionary reflecting the structure used by the datalogger
                        (input, output, timestamp). if omitted, the datalogger starts empty.
                filename (str | None, optional):
                        The base name for exported log files. this name may be augmented with
                        timestamps and format-specific extensions during export operations.
                        defaults to 'log'.

        register an at-exit handler to ensure unsaved logs are automatically persisted to
        a CSV file upon program termination.
        """
        self.persist_path = Path(persist_path) if persist_path else Path("data/logs/")
        self.log = deque(log) if log else deque()
        self.filename = filename or "log"
        atexit.register(self.save_at_exit)

    def extend(self, logs) -> None:
        if len(logs) > 0:
            log1 = convert.to_list(self.log)
            log1.extend(convert.to_list(logs))
            self.log = deque(log1)

    def append(self, *, input_data: Any, output_data: Any) -> None:
        """
        appends a new log entry, encapsulating input and output data, to the datalogger's
        record deque.

        Args:
                input_data (Any):
                        Data provided as input to a tracked operation or process.
                output_data (Any):
                        Data resulting from the operation, recorded as the output.

        constructs a log entry from the provided data and automatically includes a
        timestamp upon serialization.
        """
        log_entry = DLog(input_data=input_data, output_data=output_data)
        self.log.append(log_entry)

    def to_csv_file(
        self,
        filename: str = "log.csv",
        *,
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        flatten_=True,
        sep="[^_^]",
        index=False,
        **kwargs,
    ) -> None:
        """
        exports accumulated log entries to a CSV file, with customizable file naming
        and timestamping options.

        Args:
                filename (str, optional):
                        Filename for the CSV output, appended with '.csv' if not included, saved
                        within the specified persisting directory.
                dir_exist_ok (bool, optional):
                        If False, raises an error if the directory already exists; otherwise,
                        writes without an error.
                timestamp (bool, optional):
                        If True, appends a current timestamp to the filepath for uniqueness.
                time_prefix (bool, optional):
                        If True, place the timestamp prefix before the filepath; otherwise,
                        it's suffixed.
                verbose (bool, optional):
                        If True, print a message upon successful file save, detailing the file
                        path and number of logs saved.
                clear (bool, optional):
                        If True, empties the internal log record after saving.
                **kwargs:
                        Additional keyword arguments for pandas.DataFrame.to_csv(), allowing
                        customization of the CSV output, such as excluding the index.

        raises a ValueError with an explanatory message if an error occurs during the file
        writing or DataFrame conversion process.
        """

        if not filename.endswith(".csv"):
            filename += ".csv"

        filepath = SysUtil.create_path(
            self.persist_path,
            filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            time_prefix=time_prefix,
        )
        try:
            logs = [log.serialize(flatten_=flatten_, sep=sep) for log in self.log]
            df = convert.to_df(convert.to_list(logs, flatten=True))
            df.to_csv(filepath, index=index, **kwargs)
            if verbose:
                print(f"{len(self.log)} logs saved to {filepath}")
            if clear:
                self.log.clear()
        except Exception as e:
            raise ValueError(f"Error in saving to csv: {e}") from e

    def to_json_file(
        self,
        filename: str = "log.json",
        *,
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        flatten_=True,
        sep="[^_^]",
        index=False,
        **kwargs,
    ) -> None:
        """
        exports the log entries to a JSON file within the specified persisting directory,
        offering customization for file naming and timestamping.

        Args:
                filename (str, optional):
                        The filepath for the JSON output.'.json' is appended if not specified.
                        The file is saved within the designated persisting directory.
                timestamp (bool, optional):
                        If True, adds a timestamp to the filepath to ensure uniqueness.
                time_prefix (bool, optional):
                        Determines the placement of the timestamp in the filepath. A prefix if
                        True; otherwise, a suffix.
                dir_exist_ok (bool, optional):
                        Allows writing to an existing directory without raising an error.
                        If False, an error is raised when attempting to write to an existing
                        directory.
                verbose (bool, optional):
                         Print a message upon successful save, indicating the file path and
                        number of logs saved.
                clear (bool, optional):
                        Clears the log deque after saving, aiding in memory management.
                **kwargs:
                        Additional arguments passed to pandas.DataFrame.to_json(),
                        enabling customization of the JSON output.

        Raises:
                ValueError: When an error occurs during file writing or DataFrame conversion,
                encapsulating
                the exception with a descriptive message.

        Examples:
                Default usage saving logs to 'log.json' within the specified persisting
                directory:
                >>> datalogger.to_json_file()
                # Save path: 'data/logs/log.json'

                Custom filepath without a timestamp, using additional pandas options:
                >>> datalogger.to_json_file(filepath='detailed_log.json', orient='records')
                # Save a path: 'data/logs/detailed_log.json'
        """
        if not filename.endswith(".json"):
            filename += ".json"

        filepath = SysUtil.create_path(
            self.persist_path,
            filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            time_prefix=time_prefix,
        )

        try:
            logs = [log.serialize(flatten_=flatten_, sep=sep) for log in self.log]
            df = convert.to_df(convert.to_list(logs, flatten=True))
            df.to_json(filepath, index=index, **kwargs)
            if verbose:
                print(f"{len(self.log)} logs saved to {filepath}")
            if clear:
                self.log.clear()
        except Exception as e:
            raise ValueError(f"Error in saving to csv: {e}") from e

    def save_at_exit(self):
        """
        Registers an at-exit handler to ensure that any unsaved logs are automatically
        persisted to a file upon program termination. This safeguard helps prevent the
        loss of log data due to unexpected shutdowns or program exits.

        The method is configured to save the logs to a CSV file, named
        'unsaved_logs.csv', which is stored in the designated persisting directory. This
        automatic save operation is triggered only if there are unsaved logs present at
        the time of program exit.

        Note: This method does not clear the logs after saving, allowing for the
        possibility of manual.py review or recovery after the program has terminated.
        """
        if self.log:
            self.to_csv_file("unsaved_logs.csv", clear=False)
