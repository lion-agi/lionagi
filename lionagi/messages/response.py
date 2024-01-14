# filename: responses.py
import json
from typing import Any, Optional, Dict, List
from messages import Message
from datetime import datetime

class Response(Message):
    metadata: Dict[str, Any] = {}
    read: bool = False
    response_type: Optional[str] = None

    def __init__(self):
        super().__init__()
        self.content = {}  # Initialize content as an empty dictionary

    def _create_message(self, response: Any, name: Optional[str] = None) -> None:
        self.role = "assistant"
        try:
            response = response["message"]
            if str(response['content']) == "None":
                try:
                    tool_count = 0
                    func_list = []
                    while tool_count < len(response['tool_calls']):
                        if response['tool_calls'][tool_count]['type'] == 'function':
                            func_content = {
                                "function": ("func_" + response['tool_calls'][tool_count]['function']['name']),
                                "arguments": response['tool_calls'][tool_count]['function']['arguments']
                            }
                            func_list.append(func_content)
                        tool_count += 1

                    self.name = name or "func_request"
                    self.content['function_list'] = func_list
                    self.response_type = "function_call"
                except:
                    raise ValueError("Response message must be one of regular response or function calling")
            else:
                self.content = response['content']
                self.name = name or "assistant"
                self.response_type = "text"
        except:
            self.name = name or "func_call"
            self.content = response
            self.response_type = "unknown"

    def add_metadata(self, key: str, value: Any):
        self.metadata[key] = value
    
    def get_metadata(self):
        return self.metadata
    
    def mark_as_read(self):
        self.read = True
    
    def is_read(self):
        return self.read
    
    def set_response_type(self, response_type: str):
        self.response_type = response_type
    
    def get_response_type(self):
        return self.response_type
    
    def add_tool_call(self, tool_call: Dict[str, Any]):
        if 'tool_calls' not in self.content:
            self.content['tool_calls'] = []
        self.content['tool_calls'].append(tool_call)
    
    def remove_tool_call(self, tool_call: Dict[str, Any]):
        if 'tool_calls' in self.content:
            self.content['tool_calls'].remove(tool_call)
    
    def list_tool_calls(self):
        return self.content.get('tool_calls', [])
