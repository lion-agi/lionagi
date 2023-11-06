"""   
Copyright 2023 HaiyangLi <ocean@lionagi.ai>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
from datetime import datetime

from .sysutils import to_csv

class DataLogger:
    def __init__(self, log: list = None) -> None:
        """
        Initialize the DataLogger with an optional log list.

        Args:
            log (list, optional): List of dictionaries containing log entries. Defaults to an empty list.
        """
        self.log = log if log else []

    @staticmethod
    def _get_timestamp() -> str:
        """
        Get the current timestamp formatted as a string.

        Returns:
            str: Formatted timestamp string.

        Example:
            timestamp = self._get_timestamp()
        """
        return datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")

    @staticmethod
    def _filepath(dir_: str, filename: str, timestamp: bool = True) -> str:
        """
        Generate the filepath for saving the log.

        Args:
            dir_ (str): Directory where the file will be saved.
            filename (str): Filename for the log.
            timestamp (bool, optional): Whether to append a timestamp to the filename. Defaults to True.

        Returns:
            str: Complete filepath for saving the log.

        Example:
            filepath = self._filepath(dir_='data/logs/', filename='log.csv', timestamp=True)
        """
        os.makedirs(dir_, exist_ok=True)
        if timestamp:
            timestamp = DataLogger._get_timestamp()
            return f"{dir_}{timestamp}{filename}"
        else:
            return f"{dir_}{filename}"

    def _to_csv(self, dir_: str, filename: str, verbose: bool, timestamp: bool):
        """
        Save the log entries to a CSV file using the to_csv function.

        Args:
            dir_ (str): Directory where the log file will be saved.
            filename (str): Filename for the log.
            verbose (bool): Whether to print a message after saving.
            timestamp (bool): Whether to append a timestamp to the filename.

        Example:
            self._to_csv(dir_='data/logs/', filename='log.csv', verbose=True, timestamp=True)
        """
        filepath = self._filepath(dir_=dir_, filename=filename, timestamp=timestamp)
        to_csv(self.log, filepath)
        n_logs = len(self.log)
        self.log = []
        if verbose:
            print(f"{n_logs} logs saved to {filepath}")


class LLMLogger(DataLogger):        
    def __init__(self, log: list = None) -> None:
        """
        Initialize the LLMLogger with an optional log list.

        Args:
            log (list, optional): List of dictionaries containing log entries. Defaults to an empty list.
        """
        super().__init__(log=log)

    def __call__(self, input_, output):
        """
        Log an entry containing input and output.

        Args:
            input_: The input value.
            output: The output value.

        Example:
            logger(input="InputData", output="OutputData")
        """
        self.log.append({"input": input_, "output": output})

    def to_csv(self, dir_: str = 'data/logs/llm/', filename: str = 'llm_log.csv', verbose: bool = True, timestamp: bool = True):
        """
        Save the log entries to a CSV file.

        Args:
            dir_ (str, optional): Directory for saving the log file. Defaults to 'data/logs/llm/'.
            filename (str, optional): Filename for the log file. Defaults to 'llm_log.csv'.
            verbose (bool, optional): Whether to print a message after saving. Defaults to True.
            timestamp (bool, optional): Whether to append a timestamp to the filename. Defaults to True.

        Example:
            logger.to_csv(dir_='data/logs/llm/', filename='llm_log.csv', verbose=True, timestamp=True)
        """
        self._to_csv(dir_=dir_, filename=filename, verbose=verbose, timestamp=timestamp)


class SourceLogger(DataLogger):
    def __init__(self, log: list = None) -> None:
        """
        Initialize the SourceLogger with an optional log list.

        Args:
            log (list, optional): List of dictionaries containing log entries. Defaults to an empty list.
        """
        super().__init__(log=log)

    def __call__(self, entry: dict):
        """
        Log a dictionary entry.

        Args:
            entry (dict): The dictionary to log.

        Example:
            logger(entry={"field1": "value1", "field2": "value2"})
        """
        self.log.append(entry)

    def to_csv(self, dir_: str = 'data/logs/sources/', filename: str = 'data_log.csv', verbose: bool = True, timestamp: bool = True):
        """
        Save the log entries to a CSV file.

        Args:
            dir_ (str, optional): Directory for saving the log file. Defaults to 'data/logs/sources/'.
            filename (str, optional): Filename for the log file. Defaults to 'data_log.csv'.
            verbose (bool, optional): Whether to print a message after saving. Defaults to True.
            timestamp (bool, optional): Whether to append a timestamp to the filename. Defaults to True.

        Example:
            logger.to_csv(dir_='data/logs/sources/', filename='data_log.csv', verbose=True, timestamp=True)
        """
        self._to_csv(dir_=dir_, filename=filename, verbose=verbose, timestamp=timestamp)
