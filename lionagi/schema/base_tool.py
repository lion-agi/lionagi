
















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
            "timestamp": get_timestamp(), "level": level, **to_dict(entry)
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
            