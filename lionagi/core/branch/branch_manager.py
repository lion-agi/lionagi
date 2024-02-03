from typing import Dict, Any
from collections import deque
from enum import Enum


class RequestTitle(str, Enum):
    """
    An enumeration of valid request titles for communication requests.

    Attributes:
        MESSAGES (str): Represents a request carrying messages.
        TOOL (str): Represents a request for tool information or actions.
        SERVICE (str): Represents a request related to services.
        LLMCONFIG (str): Represents a request to configure or modify LLM settings.
    """
    MESSAGES = 'messages'
    TOOL = 'tool'
    SERVICE = 'service'
    LLMCONFIG = 'llmconfig'


class Request:
    """
    Represents a request for communication between components in the system.

    Args:
        from_name (str): The name of the sender.
        to_name (str): The name of the recipient.
        title (Union[str, RequestTitle]): The title of the request, indicating its type or category.
        request (Any): The actual content or data of the request.

    Raises:
        ValueError: If the request title is invalid or not recognized.
    """

    def __init__(self, from_name, to_name, title, request):
        self.from_ = from_name
        self.to_ = to_name
        try:
            if isinstance(title, str):
                title = RequestTitle(title)
            if isinstance(title, RequestTitle):
                self.title = title
            else:
                raise ValueError(f'Invalid request title. Valid titles are {list(RequestTitle)}')
        except:
            raise ValueError(f'Invalid request title. Valid titles are {list(RequestTitle)}')
        self.request = request


class BranchManager:
    """
    Manages branches and their communication requests within a system.

    Args:
        sources (Dict[str, Any]): Initial mapping of source names to their respective details.

    Methods:
        add_source: Adds a new source to the manager.
        delete_source: Removes a source from the manager.
        collect: Collects outgoing requests from a specified source and queues them for the recipient.
        send: Sends the queued requests to their respective recipients in the system.
    """

    def __init__(self, sources: Dict[str, Any]):
        self.sources = sources
        self.requests = {}
        for key in self.sources.keys():
            self.requests[key] = {}

    def add_source(self, sources: Dict[str, Any]):
        """
        Adds a new source or multiple sources to the manager.

        Args:
            sources (Dict[str, Any]): A dictionary mapping new source names to their details.

        Raises:
            ValueError: If any of the provided source names already exist.
        """
        for key in sources.keys():
            if key in self.sources:
                raise ValueError(f'{key} exists, please input a different name.')
            self.sources[key] = {}

    def delete_source(self, source_name):
        """
        Deletes a source from the manager by name.

        Args:
            source_name (str): The name of the source to delete.

        Raises:
            ValueError: If the specified source name does not exist.
        """
        if source_name not in self.sources:
            raise ValueError(f'{source_name} does not exist.')
        self.sources.pop(source_name)

    def collect(self, from_name):
        """
        Collects all outgoing requests from a specified source.

        Args:
            from_name (str): The name of the source from which to collect outgoing requests.

        Raises:
            ValueError: If the specified source name does not exist.
        """
        if from_name not in self.sources:
            raise ValueError(f'{from_name} does not exist.')
        while self.sources[from_name].pending_outs:
            request = self.sources[from_name].pending_outs.popleft()
            if request.from_ not in self.requests[request.to_]:
                self.requests[request.to_] = {request.from_: deque()}
            self.requests[request.to_][request.from_].append(request)

    def send(self, to_name):
        """
        Sends all queued requests to a specified recipient.

        Args:
            to_name (str): The name of the recipient to whom the requests should be sent.

        Raises:
            ValueError: If the specified recipient name does not exist or there are no requests to send.
        """
        if to_name not in self.sources:
            raise ValueError(f'{to_name} does not exist.')
        if not self.requests[to_name]:
            return
        else:
            for key in list(self.requests[to_name].keys()):
                request = self.requests[to_name].pop(key)
                if key not in self.sources[to_name].pending_ins:
                    self.sources[to_name].pending_ins[key] = request
                else:
                    self.sources[to_name].pending_ins[key].append(request)

