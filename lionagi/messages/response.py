from typing import Any, Optional
from .message import Message

class Response(Message):

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
                    self.content = {'function_list': func_list}
                except:
                    raise ValueError("Response message must be one of regular response or function calling")
            else:
                self.content = response['content']
                self.name = name or "assistant"
        except:
            self.name = name or "func_call"
            self.content = response
        