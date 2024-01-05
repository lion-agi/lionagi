import json
from typing import Any, Optional
from ..schema import BaseNode


class Message(BaseNode):

    role: Optional[str] = None
    name: Optional[str] = None
    
    def _to_message(self):
        out = {
            "role": self.role,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
        return out

    def _create_role_message(self, role_: str, 
                             content: Any, 
                             content_key: str, 
                             name: Optional[str] = None
                             ) -> None:
        self.role = role_
        self.content = {content_key: content}
        self.name = name or role_


class System(Message):
    
    def _create_message(self, system: Any, name: Optional[str] = None) -> None:
        self._create_role_message(role_="system", content_key="system", content=system, name=name)
    
    
class Instruction(Message):

    def _create_message(self, instruction: Any, context=None ,name: Optional[str] = None) -> None:
        self._create_role_message(role_="user", content_key="instruction", content=instruction, name=name)
        if context: 
            self.content.update({"context": context})
    
    
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

        