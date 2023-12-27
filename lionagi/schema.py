import json
from collections import deque
from typing import Any, Dict, Optional, Union

from .utils.sys_utils import create_id, create_path, to_csv
from pydantic import BaseModel, Field

# checked --------------------------------------------------------
class BaseNode(BaseModel):
    id_: str = Field(default_factory=lambda: str(create_id()), alias="node_id")
    content: Union[str, Dict[str, Any], None, int] = None
    metadata: Union[Dict[str, Any], None] = Field(default_factory=dict)

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__

    def to_json(self) -> str:
        return json.dumps(self.model_dump(by_alias=True))

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True)

    @classmethod
    def from_json(cls, json_str: str) -> "BaseNode":
        data = json.loads(json_str)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseNode":
        return cls(**data)

    def add_meta(self, replace=True, **kwags) -> None:
        if replace:
            self.metadata.update(**kwags)
        else: 
            for k, v in kwags.items():
                if k in self.metadata.keys():
                    raise ValueError(f"Key already existed")
                if k not in self.metadata.keys():
                    self.metadata.update({k:v})
    
    def set_meta(self, metadata_: dict) -> None:
        self.metadata = metadata_
    
    def set_content(self, content: Union[str, Dict[str, Any], None]):
        self.content = content

    def set_id(self, id: str):
        self.id_ = id

    def get_meta(self):
        return self.metadata
    
    def get_content(self):
        return self.content
    
    def get_id(self):
        return self.id_

class ConditionalRelationship(BaseNode):
    target_node_id: str
    condition: Optional(Dict) = None
    label: str = None

    def condition_existed(self, condition_key):
        if self.condition:
            try:
                self.condition.get(condition_key)
                return True
            except:
                return False
        return False

    def get_condition(self, condition_key) -> bool:
        if self.condition_existed(condition_key=condition_key):
            a = self.condition.get(condition_key)
            if a is not None and str(a).strip().lower() != 'none':
                return a
        else: 
            raise ValueError(f"Condition {condition_key} has no value")


class DataNode(BaseNode):
    
    ...
    # def from_llama(self, data_:, **kwags):
    #     ...
        
    # def to_llama(self, **kwags):
    #     # to llama_index textnode
    #     ...
        
    # def from_langchain(self, data_, **kwags):
    #     ...
    
    # def to_langchain(self, **kwags):
    #     ...
        
    # def to_csv(self, **kwags):
    #     ...

    # def __call__(self, file_=None):
    #     ...


class MessageNode(BaseNode):
    role: str
    name: str
    
    # def from_oai(self):
    #     ...


class File(DataNode):
    ...
    
    # def from_path(self, path_, reader, clean=True, **kwags):
    #     self.content = reader(path_=path_, clean=clean, **kwags)
    
    # def to_chunks(self, chunker, **kwags):
    #     ...


class Chunk(DataNode):
    ...    
    # @classmethod
    # def from_files(cls, files):
    #     ...    
    
    # @classmethod
    # def to_files(cls):
    #     ...
    
    
class DataLogger:
    """
    Logs data entries and outputs them to a CSV file.
    
    This class provides a logging mechanism for data entries that can be saved to a
    CSV file. It offers methods for appending new log entries, saving the log to a CSV file,
    and setting the directory where the logs should be saved.

    Attributes:
        dir (str):
            The directory where the log files are to be saved.
        log (deque):
            A deque that stores log entries.

    Methods:
        __call__(entry):
            Appends a new entry to the log.
        to_csv(dir: str, filename: str, verbose: bool, timestamp: bool, dir_exist_ok: bool, file_exist_ok: bool): 
            Converts the log to a CSV format and saves it to a file.
        set_dir(dir: str):
            Sets the directory for saving log files.
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

    def to_csv(self,  filename: str, dir: any=None, verbose: bool = True, timestamp: bool = True, dir_exist_ok=True, file_exist_ok=False):
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

# checked --------------------------------------------------------