from abc import ABC
from typing import TypeVar

from lionagi.libs.sys_util import PATH_TYPE, SysUtil
from lionagi.libs.ln_api import BaseService
from lionagi.libs import ln_dataframe as dataframe

from lionagi.core.schema.base_node import TOOL_TYPE, Tool
from lionagi.core.schema.data_logger import DataLogger, DLog
from lionagi.core.tool.tool_manager import ToolManager

T = TypeVar("T", bound=Tool)


class BranchIOMixin(ABC):
    @classmethod
    def _from_csv(cls, filename: str, read_kwargs: dict | None = None, **kwargs) -> "T":
        """Internal helper method to create an instance from a CSV file.

        Args:
            filename (str): Path to the CSV file.
            read_kwargs (dict | None): Additional keyword arguments for `dataframe.read_csv`.
            **kwargs: Additional keyword arguments passed to the class constructor.

        Returns:
            T: An instance of the class initialized with messages from the CSV file.
        """
        read_kwargs = {} if read_kwargs is None else read_kwargs
        messages = dataframe.read_csv(filename, **read_kwargs)
        return cls(messages=messages, **kwargs)

    @classmethod
    def from_csv(
        cls,
        filepath,
        branch_name: str | None = None,
        service: BaseService | None = None,
        llmconfig: dict[str, str | int | dict] | None = None,
        tools: TOOL_TYPE | None = None,
        datalogger: None | DataLogger = None,
        persist_path: PATH_TYPE | None = None,
        tool_manager: ToolManager | None = None,
        read_kwargs=None,
        **kwargs,
    ):
        """Creates an instance from a CSV file, initializing it with provided arguments.

        Args:
            filepath (str): Path to the CSV file to load messages from.
            branch_name (str | None): Name of the branch.
            service (BaseService | None): Service associated with the branch.
            llmconfig (dict[str, str | int | dict] | None): Configuration for LLM.
            tools (TOOL_TYPE | None): Tools to be used in the branch.
            datalogger (DataLogger | None): Logger for branch operations.
            persist_path (PATH_TYPE | None): Path for data persistence.
            tool_manager (ToolManager | None): Manager for handling tools.
            read_kwargs (dict | None): Additional keyword arguments for `dataframe.read_csv`.
            **kwargs: Additional keyword arguments for branch initialization.

        """

        self = cls._from_csv(
            filepath=filepath,
            read_kwargs=read_kwargs,
            branch_name=branch_name,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            tool_manager=tool_manager,
            **kwargs,
        )

        return self

    @classmethod
    def from_json_string(
        cls,
        filepath,
        branch_name: str | None = None,
        service: BaseService | None = None,
        llmconfig: dict[str, str | int | dict] | None = None,
        tools: TOOL_TYPE | None = None,
        datalogger: None | DataLogger = None,
        persist_path: PATH_TYPE | None = None,
        tool_manager: ToolManager | None = None,
        read_kwargs=None,
        **kwargs,
    ):
        """Creates an instance from a JSON string, initializing it with provided arguments.

        Args:
            filepath (str): Path to the JSON file to load messages from.
            branch_name (str | None): Name of the branch.
            service (BaseService | None): Service associated with the branch.
            llmconfig (dict[str, str | int | dict] | None): Configuration for LLM.
            tools (TOOL_TYPE | None): Tools to be used in the branch.
            datalogger (DataLogger | None): Logger for branch operations.
            persist_path (PATH_TYPE | None): Path for data persistence.
            tool_manager (ToolManager | None): Manager for handling tools.
            read_kwargs (dict | None): Additional keyword arguments for `dataframe.read_json`.
            **kwargs: Additional keyword arguments for branch initialization.
        """
        self = cls._from_json(
            filepath=filepath,
            read_kwargs=read_kwargs,
            branch_name=branch_name,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            tool_manager=tool_manager,
            **kwargs,
        )

        return self

    @classmethod
    def _from_json(cls, filename: str, read_kwargs=None, **kwargs) -> "T":
        """
        Internal helper method to create an instance from a JSON file.

        Args:
            filename (str): Path to the JSON file.
            read_kwargs (dict | None): Additional keyword arguments for `dataframe.read_json`.
            **kwargs: Additional keyword arguments passed to the class constructor.

        """
        read_kwargs = {} if read_kwargs is None else read_kwargs
        messages = dataframe.read_json(filename, **read_kwargs)
        return cls(messages=messages, **kwargs)

    def to_csv_file(
        self,
        filename: PATH_TYPE = "messages.csv",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        **kwargs,
    ) -> None:
        """Exports the branch messages to a CSV file.

        Allows specifying the file name, directory behavior, timestamping options, and whether to clear
        messages post-export. Supports additional pandas.DataFrame.to_csv keyword arguments.

        Args:
            filename (PATH_TYPE): Destination path for the CSV file. Defaults to 'messages.csv'.
            dir_exist_ok (bool): If False, an error is raised if the directory exists. Defaults to True.
            timestamp (bool): If True, appends a timestamp to the filename. Defaults to True.
            time_prefix (bool): If True, prefixes the filename with a timestamp. Defaults to False.
            verbose (bool): If True, prints a message upon successful export. Defaults to True.
            clear (bool): If True, clears the messages after exporting. Defaults to True.
            **kwargs: Additional keyword arguments for pandas.DataFrame.to_csv.

        Raises:
            ValueError: If there is an error in saving to CSV.
        """

        if not filename.endswith(".csv"):
            filename += ".csv"

        filename = SysUtil.create_path(
            self.datalogger.persist_path,
            filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            time_prefix=time_prefix,
        )

        try:
            self.messages.to_csv(filename, **kwargs)
            if verbose:
                print(f"{len(self.messages)} messages saved to {filename}")
            if clear:
                self.clear_messages()
        except Exception as e:
            raise ValueError(f"Error in saving to csv: {e}")

    def to_json_file(
        self,
        filename: PATH_TYPE = "messages.json",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        **kwargs,
    ) -> None:
        """
        Exports branch messages to a JSON file.

        Args:
            filename (PATH_TYPE): Destination path for the JSON file. Defaults to 'messages.json'.
            dir_exist_ok (bool): If False, raises an error if the directory exists. Defaults to True.
            timestamp (bool): If True, appends a timestamp to the filename. Defaults to True.
            time_prefix (bool): If True, prefixes the filename with a timestamp. Defaults to False.
            verbose (bool): If True, prints a message upon successful export. Defaults to True.
            clear (bool): If True, clears the messages after exporting. Defaults to True.
            **kwargs: Additional keyword arguments for `pandas.DataFrame.to_json()`.

        Examples:
            >>> branch.to_json_file(filename="branch_messages.json", timestamp=True)
        """

        if not filename.endswith(".json"):
            filename += ".json"

        filename = SysUtil.create_path(
            self.datalogger.persist_path,
            filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            time_prefix=time_prefix,
        )

        try:
            self.messages.to_json(
                filename, orient="records", lines=True, date_format="iso", **kwargs
            )
            if verbose:
                print(f"{len(self.messages)} messages saved to {filename}")
            if clear:
                self.clear_messages()
        except Exception as e:
            raise ValueError(f"Error in saving to json: {e}")

    def log_to_csv(
        self,
        filename: PATH_TYPE = "log.csv",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        flatten_=True,
        sep: str | None = "[^_^]",
        **kwargs,
    ) -> None:
        """Exports the data logger contents to a CSV file.

        Configurable for file naming, directory existence checks, timestamping, verbosity, clearing log post-export,
        and flattening of the log data. Additional DataFrame.to_csv kwargs can be passed.

        Args:
            filename (PATH_TYPE): Destination path for the CSV file. Defaults to 'log.csv'.
            dir_exist_ok (bool): If False, raises an error if the directory exists. Defaults to True.
            timestamp (bool): If True, appends a timestamp to the filename. Defaults to True.
            time_prefix (bool): If True, prefixes the filename with a timestamp. Defaults to False.
            verbose (bool): If True, prints a message upon successful export. Defaults to True.
            clear (bool): If True, clears the logger after exporting. Defaults to True.
            flatten_ (bool): If True, flattens the data logger contents. Defaults to True.
            sep (str): Separator used in flattening process. Defaults to "[^_^]".
            **kwargs: Additional keyword arguments for pandas.DataFrame.to_csv.

        Raises:
            ValueError: If there is an error in saving to CSV.
        """
        self.datalogger.to_csv_file(
            filename=filename,
            dir_exist_ok=dir_exist_ok,
            timestamp=timestamp,
            time_prefix=time_prefix,
            verbose=verbose,
            clear=clear,
            flatten_=flatten_,
            sep=sep,
            **kwargs,
        )

    def log_to_json(
        self,
        filename: PATH_TYPE = "log.json",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        flatten_=True,
        sep="[^_^]",
        **kwargs,
    ) -> None:
        """Exports the data logger contents to a JSON file.

        Offers configuration options for file naming, directory checks, timestamping, verbosity, clearing log post-export,
        and data flattening. Additional DataFrame.to_json kwargs can be passed.

        Args:
            filename (PATH_TYPE): Destination path for the JSON file. Defaults to 'log.json'.
            dir_exist_ok (bool): If False, raises an error if the directory exists. Defaults to True.
            timestamp (bool): If True, appends a timestamp to the filename. Defaults to True.
            time_prefix (bool): If True, prefixes the filename with a timestamp. Defaults to False.
            verbose (bool): If True, prints a message upon successful export. Defaults to True.
            clear (bool): If True, clears the logger after exporting. Defaults to True.
            flatten_ (bool): If True, flattens the data logger contents. Defaults to True.
            sep (str): Separator used in flattening process. Defaults to "[^_^]".
            **kwargs: Additional keyword arguments for pandas.DataFrame.to_json.

        Raises:
            ValueError: If there is an error in saving to JSON.
        """

        self.datalogger.to_json_file(
            filename=filename,
            dir_exist_ok=dir_exist_ok,
            timestamp=timestamp,
            time_prefix=time_prefix,
            verbose=verbose,
            clear=clear,
            flatten_=flatten_,
            sep=sep,
            **kwargs,
        )

    def load_log(
        self,
        filename: str,
        flattened=True,
        sep: str | None = "[^_^]",
        verbose=True,
        **kwargs,
    ):
        """
        Loads log data from a specified file into the branch's data logger.

        This method supports loading log data from both CSV and JSON formats. It deserializes
        each log entry using the specified separator and flattening option before appending
        it to the branch's log.

        Args:
            filename (str): The path to the file from which log data is to be loaded.
            flattened (bool): Specifies whether the log data should be unflattened upon loading.
                              Defaults to True, meaning the log data will be unflattened if it was
                              previously flattened.
            sep (str): The separator used in the log data. This is only relevant if `flattened` is True.
                       Defaults to "[^_^]".
            verbose (bool): If True, prints the number of log entries loaded upon completion.
                            Defaults to True.
            **kwargs: Additional keyword arguments to pass to the underlying read function,
                      `dataframe.read_csv` or `dataframe.read_json`, depending on the file extension.

        Raises:
            ValueError: If there's an error during the loading process, such as an issue with
                        the file format or the deserialization process.

        Examples:
            >>> branch.load_log("logs.csv", verbose=True)
            >>> branch.load_log("logs.json", flattened=False, sep="|", verbose=True)
        """
        df = ""
        try:
            if filename.endswith(".csv"):
                df = dataframe.read_csv(filename, **kwargs)

            elif filename.endswith(".json"):
                df = dataframe.read_json(filename, **kwargs)

            for _, row in df.iterrows():
                self.datalogger.log.append(
                    DLog.deserialize(
                        input_str=row.input_data,
                        output_str=row.output_data,
                        unflatten_=flattened,
                        sep=sep,
                    )
                )

            if verbose:
                print(f"Loaded {len(df)} logs from {filename}")
        except Exception as e:
            raise ValueError(f"Error in loading log: {e}")
