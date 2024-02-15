from collections import deque
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Callable
from ..utils.sys_util import get_timestamp, create_path, as_dict, to_df, create_id, change_dict_key, is_schema
import json
import xml.etree.ElementTree as ET

from pydantic import BaseModel, Field, AliasChoices, field_serializer

T = TypeVar('T', bound='BaseNode')


class BaseNode(BaseModel):
    """
    The base class for nodes containing general information and metadata.

    Attributes:
        id_ (str): The unique identifier for the node.
        metadata (Dict[str, Any]): Additional metadata for the node.
        label (Optional[str]): An optional label for the node.
        related_nodes (List[str]): List of related node IDs.
        content (Union[str, Dict[str, Any], None, Any]): The content of the node.

    Examples:
        >>> node = BaseNode(content="Example content")
        >>> node_dict = node.to_dict()
        >>> json_str = node.to_json()
        >>> same_node = BaseNode.from_json(json_str)
    """
    
    id_: str = Field(default_factory=lambda: str(create_id()), alias="node_id")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    label: Optional[str] = None
    related_nodes: List[str] = Field(default_factory=list)
    content: Union[str, Dict[str, Any], None, Any] = Field(
        default=None, validation_alias=AliasChoices('text', 'page_content', 'chunk_content')
    )

    class Config:
        extra = 'allow'
        populate_by_name = True
        validate_assignment = True
        validate_return = True
        str_strip_whitespace = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        """
        Creates an instance of the class from a dictionary.

        Args:
            data: A dictionary containing the node's data.

        Returns:
            An instance of the class.

        Examples:
            >>> data = {"content": "Example content"}
            >>> node = BaseNode.from_dict(data)
        """
        return cls(**data)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        """
        Creates an instance of the class from a JSON string.

        Args:
            json_str: A JSON string containing the node's data.
            **kwargs: Additional keyword arguments to pass to json.loads.

        Returns:
            An instance of the class.

        Examples:
            >>> json_str = '{"content": "Example content"}'
            >>> node = BaseNode.from_json(json_str)
        """
        try:
            data = json.loads(json_str, **kwargs)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string provided for deserialization.") from e

    @classmethod
    def from_xml(cls, xml_str: str) -> T:
        """
        Creates an instance of the class from an XML string.

        Args:
            xml_str: An XML string containing the node's data.

        Returns:
            An instance of the class.

        Examples:
            >>> xml_str = "<BaseNode><content>Example content</content></BaseNode>"
            >>> node = BaseNode.from_xml(xml_str)
        """
        root = ET.fromstring(xml_str)
        data = cls._xml_to_dict(root)
        return cls(**data)

    def to_json(self) -> str:
        """
        Converts the instance to a JSON string.

        Returns:
            A JSON string representing the node.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> json_str = node.to_json()
        """
        return self.model_dump_json(by_alias=True)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the instance to a dictionary.

        Returns:
            A dictionary representing the node.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> node_dict = node.to_dict()
        """
        return self.model_dump(by_alias=True)

    def to_xml(self) -> str:
        """
        Converts the instance to an XML string.

        Returns:
            An XML string representing the node.

        Examples:
            >>> node = BaseNode(content="Example content")
            >>> xml_str = node.to_xml()
        """
        root = ET.Element(self.__class__.__name__)
        for attr, value in self.to_dict().items():
            child = ET.SubElement(root, attr)
            child.text = str(value)
        return ET.tostring(root, encoding='unicode')

    def validate_content(self, schema: Dict[str, type]) -> bool:
        """
        Validates the node's content against a schema.

        Args:
            schema: The schema to validate against.

        Returns:
            True if the content matches the schema, False otherwise.

        Examples:
            >>> schema = {"title": str, "body": str}
            >>> node = BaseNode(content={"title": "Example", "body": "Content"})
            >>> node.validate_content(schema)
        """
        if not isinstance(self.content, dict):
            return False
        return is_schema(self.content, schema)

    @property
    def meta_keys(self) -> List[str]:
        """
        List of metadata keys.

        Returns:
            A list of keys in the metadata dictionary.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.meta_keys
        """
        return list(self.metadata.keys())

    def has_meta_key(self, key: str) -> bool:
        """
        Checks if a metadata key exists.

        Args:
            key: The metadata key to check for.

        Returns:
            True if the key exists, False otherwise.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.has_meta_key("author")
        """
        return key in self.metadata

    def get_meta_key(self, key: str) -> Any:
        """
        Retrieves a value from the metadata dictionary.

        Args:
            key: The key for the value to retrieve.

        Returns:
            The value associated with the key, if it exists.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.get_meta_key("author")
        """
        return self.metadata.get(key)

    def change_meta_key(self, old_key: str, new_key: str) -> bool:
        """
        Changes a key in the metadata dictionary.

        Args:
            old_key: The old key name.
            new_key: The new key name.

        Returns:
            True if the key was changed successfully, False otherwise.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.change_meta_key("author", "creator")
        """
        if old_key in self.metadata:
            change_dict_key(self.metadata, old_key=old_key, new_key=new_key)
            return True
        return False

    def delete_meta_key(self, key: str) -> bool:
        """
        Deletes a key from the metadata dictionary.

        Args:
            key: The key to delete.

        Returns:
            True if the key was deleted, False otherwise.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.delete_meta_key("author")
        """
        if key in self.metadata:
            del self.metadata[key]
            return True
        return False
            
    def merge_meta(self, other_metadata: Dict[str, Any], overwrite: bool = False) -> None:
        """
        Merges another metadata dictionary into the current metadata.

        Args:
            other_metadata: The metadata dictionary to merge.
            overwrite: If True, existing keys will be overwritten.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> new_meta = {"editor": "Jane Smith"}
            >>> node.merge_meta(new_meta)
        """
        if not overwrite:
            other_metadata = ({
                k: v for k, v in other_metadata.items() 
                if k not in self.metadata
            })
        self.metadata.update(other_metadata)

    def clear_meta(self) -> None:
        """
        Clears the metadata dictionary.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe"})
            >>> node.clear_meta()
        """

        self.metadata.clear()

    def filter_meta(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        """
        Filters the metadata dictionary based on a filter function.

        Args:
            filter_func: The function to filter metadata items.

        Returns:
            A dictionary containing the filtered metadata items.

        Examples:
            >>> node = BaseNode(metadata={"author": "John Doe", "year": 2020})
            >>> filtered_meta = node.filter_meta(lambda x: isinstance(x, str))
        """
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def validate_meta(self, schema: Dict[str, type]) -> bool:
        """
        Validates the metadata against a schema.

        Args:
            schema: The schema to validate against.

        Returns:
            True if the metadata matches the schema, False otherwise.

        Examples:
            >>> schema = {"author": str, "year": int}
            >>> node = BaseNode(metadata={"author": "John Doe", "year": 2020})
            >>> node.validate_meta(schema)
        """
        
        return is_schema(dict_=self.metadata, schema=schema)

    def add_related_node(self, node_id: str) -> bool:
        """
        Adds a related node ID to the list of related nodes.

        Args:
            node_id: The ID of the related node to add.

        Returns:
            True if the ID was added, False if it was already in the list.

        Examples:
            >>> node = BaseNode()
            >>> related_node_id = "123456"
            >>> node.add_related_node(related_node_id)
        """
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)
            return True
        return False

    def remove_related_node(self, node_id: str) -> bool:
        """
        Removes a related node ID from the list of related nodes.

        Args:
            node_id: The ID of the related node to remove.

        Returns:
            True if the ID was removed, False if it was not in the list.

        Examples:
            >>> node = BaseNode(related_nodes=["123456"])
            >>> related_node_id = "123456"
            >>> node.remove_related_node(related_node_id)
        """
        if node_id in self.related_nodes:
            self.related_nodes.remove(node_id)
            return True
        return False

    def __str__(self) -> str:
        """String representation of the BaseNode instance."""
        content_preview = (str(self.content)[:75] + '...') if len(str(self.content)) > 75 else str(self.content)
        metadata_preview = str(self.metadata)[:75] + '...' if len(str(self.metadata)) > 75 else str(self.metadata)
        related_nodes_preview = ', '.join(self.related_nodes[:3]) + ('...' if len(self.related_nodes) > 3 else '')
        return (f"{self.__class__.__name__}(id={self.id_}, label={self.label}, "
                f"content='{content_preview}', metadata='{metadata_preview}', "
                f"related_nodes=[{related_nodes_preview}])")

    def __repr__(self):
        """Machine-readable representation of the BaseNode instance."""
        return f"{self.__class__.__name__}({self.to_json()})"

    @staticmethod
    def _xml_to_dict(root: ET.Element) -> Dict[str, Any]:
        data = {}
        for child in root:
            data[child.tag] = child.text
        return data

class Tool(BaseNode):
    """
    A class representing a tool with a function, content, parser, and schema.

    Attributes:
        func (Callable): The function associated with the tool.
        content (Any, optional): The content to be processed by the tool. Defaults to None.
        parser (Any, optional): The parser to be used with the tool. Defaults to None.
        schema_ (Dict): The schema definition for the tool.

    Examples:
        >>> tool = Tool(func=my_function, schema_={'type': 'string'})
        >>> serialized_func = tool.serialize_func()
        >>> print(serialized_func)
        'my_function'
    """

    func: Any
    content: Any = None
    parser: Any = None
    schema_: dict

    @field_serializer('func')
    def serialize_func(self, func):
        """
        Serialize the function to its name.

        Args:
            func (Callable): The function to serialize.

        Returns:
            str: The name of the function.

        Examples:
            >>> def my_function():
            ...     pass
            >>> Tool.serialize_func(my_function)
            'my_function'
        """
        return func.__name__


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
        self.dir = dir or 'data/logs/'
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
        self, filename: str ='log.csv', 
        file_exist_ok: bool = False,  
        timestamp = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear = True, **kwargs
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
        try:
            df = to_df(list(self.log))
            df.to_csv(filepath, **kwargs)
            if verbose:
                print(f"{len(self.log)} logs saved to {filepath}")
            if clear:
                self.log.clear()
        except Exception as e:
            raise ValueError(f"Error in saving to csv: {e}")
        
    def to_json(
        self, filename: str = 'log.json', 
        timestamp = False, 
        time_prefix=False,
        file_exist_ok: bool = False, 
        verbose: bool = True, 
        clear = True, 
        **kwargs
    ) -> None:
        """
        Exports the logged data to a JSONL file and optionally clears the log.

        Parameters:
            filename (str): The name of the JSONL file.
            file_exist_ok (bool): If True, creates the directory for the file if it does not exist. Defaults to False.
            verbose (bool): If True, prints a message upon completion. Defaults to True.
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = create_path(
            self.dir, filename, timestamp=timestamp, 
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

class DataNode(BaseNode):

    def to_llama_index(self, **kwargs) -> Any:
        """
        Converts node to llama index format.

        Args:
            **kwargs: Variable length argument list.

        Returns:
            The llama index representation of the node.

        Examples:
            node = DataNode()
            llama_index = node.to_llama_index()
        """
        from lionagi.bridge.llama_index import to_llama_index_textnode
        return to_llama_index_textnode(self, **kwargs)

    def to_langchain(self, **kwargs) -> Any:
        """
        Converts node to langchain document format.

        Args:
            **kwargs: Variable length argument list.

        Returns:
            The langchain document representation of the node.

        Examples:
            node = DataNode()
            langchain_doc = node.to_langchain()
        """
        from lionagi.bridge.langchain import to_langchain_document
        return to_langchain_document(self, **kwargs)

    @classmethod
    def from_llama_index(cls, llama_node: Any, **kwargs) -> "DataNode":
        """
        Creates a DataNode instance from a llama index node.

        Args:
            llama_node: The llama index node object.
            **kwargs: Variable length argument list.

        Returns:
            An instance of DataNode.

        Examples:
            llama_node = SomeLlamaIndexNode()
            data_node = DataNode.from_llama_index(llama_node)
        """
        llama_dict = llama_node.to_dict(**kwargs)
        return cls.from_dict(llama_dict)

    @classmethod
    def from_langchain(cls, lc_doc: Any) -> "DataNode":
        """
        Creates a DataNode instance from a langchain document.

        Args:
            lc_doc: The langchain document object.

        Returns:
            An instance of DataNode.

        Examples:
            lc_doc = SomeLangChainDocument()
            data_node = DataNode.from_langchain(lc_doc)
        """
        info_json = lc_doc.to_json()
        info_node = {'lc_id': info_json['id']}
        info_node = {**info_node, **info_json['kwargs']}
        return cls(**info_node)


class File(DataNode):

    ...
    

class Chunk(DataNode):

    ...    

from dataclasses import dataclass


# credit to OpenAI for the following object
@dataclass
class StatusTracker:
    """
    Class for keeping track of various task statuses.
    
    This class serves as a simple way to monitor different types of task
    outcomes and errors within a system. It uses dataclasses for easy
    creation and management of state.
    
    Attributes:
        num_tasks_started:
            The number of tasks that have been initiated.
        num_tasks_in_progress:
            The number of tasks currently being processed.
        num_tasks_succeeded:
            The number of tasks that have completed successfully.
        num_tasks_failed:
            The number of tasks that have failed.
        num_rate_limit_errors:
            The number of tasks that failed due to rate limiting.
        num_api_errors:
            The number of tasks that failed due to API errors.
        num_other_errors:
            The number of tasks that failed due to other errors.
    """
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0

# import asyncio
# from typing import Any, Callable
# from ..utils.call_util import tcall

# class AsyncQueue:
#     """
#     A queue class that handles asynchronous operations using asyncio.

#     This class provides an asynchronous queue that can enqueue items, process them
#     asynchronously, and support graceful shutdowns. It is designed to facilitate
#     concurrent task processing in an orderly and controlled manner.

#     Attributes:
#         queue (asyncio.Queue):
#             A queue to hold items for asynchronous processing.
#         _stop_event (asyncio.Event):
#             An event to signal when the queue should stop processing.

#     Methods:
#         enqueue(item):
#             Add an item to the queue for processing.
#         dequeue():
#             Remove and return an item from the queue.
#         join():
#             Wait until all items in the queue have been processed.
#         stop():
#             Signal to stop processing new items in the queue.
#         stopped():
#             Check if the queue has been signaled to stop.
#         process_requests(func):
#             Process items using a provided function.
#     """

#     def __init__(self) -> None:
#         """
#         Initializes an AsyncQueue object with an empty asyncio Queue and a stop event.
#         """
#         self.queue = asyncio.Queue()
#         self._stop_event = asyncio.Event()

#     async def enqueue(self, item: Any) -> None:
#         """
#         Asynchronously add an item to the queue for processing.

#         Parameters:
#             item (Any): The item to be added to the queue.

#         Example:
#             >>> async_queue = AsyncQueue()
#             >>> asyncio.run(async_queue.enqueue('Task 1'))
#         """
#         await self.queue.put(item)

#     async def dequeue(self) -> Any:
#         """
#         Asynchronously remove and return an item from the queue.

#         If the queue is empty, this method will wait until an item is available.

#         Returns:
#             Any: The next item from the queue.

#         Example:
#             >>> async_queue = AsyncQueue()
#             >>> asyncio.run(async_queue.enqueue('Task 1'))
#             >>> asyncio.run(async_queue.dequeue())
#             'Task 1'
#         """
#         return await self.queue.get()

#     async def join(self) -> None:
#         """
#         Asynchronously wait until all items in the queue have been processed.

#         This method blocks until every item that has been enqueued is processed, 
#         ensuring that all tasks are completed.

#         Example:
#             >>> async_queue = AsyncQueue()
#             >>> asyncio.run(async_queue.enqueue('Task 1'))
#             >>> asyncio.run(async_queue.join())  # This will block until 'Task 1' is processed.
#         """
#         await self.queue.join()

#     async def stop(self) -> None:
#         """
#         Signal the queue to stop processing new items.

#         Once called, the queue will not process any new items after the current ones
#         are completed, allowing for a graceful shutdown.

#         Example:
#             >>> async_queue = AsyncQueue()
#             >>> asyncio.run(async_queue.stop())  # This signals the queue to stop processing.
#         """
#         self._stop_event.set()

#     def stopped(self) -> bool:
#         """
#         Check if the queue has been signaled to stop processing.

#         Returns:
#             bool: True if a stop has been signaled, False otherwise.

#         Example:
#             >>> async_queue = AsyncQueue()
#             >>> asyncio.run(async_queue.stop())
#             >>> async_queue.stopped()
#             True
#         """
#         return self._stop_event.is_set()

#     # async def process_requests(self, func: Callable[[Any], Any]) -> None:
#     #     """
#     #     Asynchronously process items from the queue using the provided function.

#     #     Continuously dequeues items and applies the given function to each. 
#     #     The processing stops when the queue is signaled to stop or a sentinel value (`None`) is dequeued.

#     #     Parameters:
#     #         func (Callable[[Any], Any]): A coroutine function to process items from the queue.

#     #     Example:
#     #         >>> async def sample_processing(task):
#     #         ...     print("Processing:", task)
#     #         >>> async_queue = AsyncQueue()
#     #         >>> asyncio.run(async_queue.enqueue('Task 1'))
#     #         >>> asyncio.run(async_queue.process_requests(sample_processing))
#     #         Processing: Task 1
#     #     """
#     #     while not self.stopped():
#     #         item = await self.dequeue()
#     #         if item is None:  # Using `None` as a sentinel value to cease processing.
#     #             await self.stop()
#     #             break
#     #         await func(item)
            
#     async def process_requests(self, func, timeout=None):
#         """
#         Process items with timeout management for each task.
#         """
#         tasks = set()
#         while not self.stopped():
#             if len(tasks) >= self.max_concurrent_tasks:
#                 done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

#             item = await self.dequeue()
#             if item is None:
#                 await self.stop()
#                 break

#             # Wrap the function call with tcall for timeout handling
#             task = asyncio.create_task(tcall(item, func, timeout=timeout))
#             tasks.add(task)

#         if tasks:
#             await asyncio.wait(tasks)
            