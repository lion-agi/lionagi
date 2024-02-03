from typing import Dict, Any
from collections import deque
from enum import Enum


class RequestTitle(str, Enum):
    MESSAGES = 'messages'
    TOOL = 'tool'
    SERVICE = 'service'
    LLMCONFIG = 'llmconfig'


class Request:

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

    def __init__(self, sources: Dict[str, Any]):
        self.sources = sources
        self.requests = {}
        for key in self.sources.keys():
            self.requests[key] = {}

    def add_source(self, sources: Dict[str, Any]):
        for key in sources.keys():
            if key in self.sources:
                raise ValueError(f'{key} exists, please input a different name.')
            self.sources[key] = {}

    def delete_source(self, source_name):
        if source_name not in self.sources:
            raise ValueError(f'{source_name} does not exist.')
        self.sources.pop(source_name)

    def collect(self, from_name):
        if from_name not in self.sources:
            raise ValueError(f'{from_name} does not exist.')
        while self.sources[from_name].pending_outs:
            request = self.sources[from_name].pending_outs.popleft()
            if request.from_ not in self.requests[request.to_]:
                self.requests[request.to_] = {request.from_: deque()}
            self.requests[request.to_][request.from_].append(request)

    def send(self, to_name):
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

