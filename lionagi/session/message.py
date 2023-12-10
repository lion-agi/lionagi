from datetime import datetime
import json
from ..utils.sys_util import create_id
from ..utils.log_util import DataLogger


class Message:

    def __init__(self) -> None:
        self.role = None
        self.content = None
        self.name = None
        self.metadata = None
        self._logger = DataLogger()
    
    def create_message(self, system=None, instruction=None, context=None, response=None, name=None):
        
        if (system and (response or instruction)) or (response and instruction):
            raise ValueError("Error: Message cannot have more than one role.")
        
        else: 
            if response:
                response = response["message"]
                if str(response['content']) == "None":
                    try:
                        # currently can only support a single function as tool
                        if response['tool_calls'][0]['type'] == 'function':
                            self.role = "tool"
                            self.name = name or ("func_" + response['tool_calls'][0]['function']['name'])
                            content = response['tool_calls'][0]['function']['arguments']
                            self.content = {"function":self.name, "arguments": content}
                    except:
                        raise ValueError("Response message must have content from assistant or tools")
                else:
                    self.role = "assistant"
                    self.content = response['content']
                    self.name = name or "assistant"
            elif instruction:
                self.role = "user"
                self.content = {"instruction": instruction}
                self.name = name or "user"
                if context:
                    self.content.update({"context": context})
            elif system:
                self.role = "system"
                self.content = system
                self.name = name or "system"
    
    def to_json(self):
        
        out = {
            "role": self.role,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
    
        self.metadata = {
            "id": create_id(),
            "timestamp": datetime.now().isoformat(),
            "name": self.name}
        
        self._logger({**self.metadata, **out})
        return out
        
    def __call__(self, system=None, instruction=None, context=None, response=None, name=None):
        self.create_message(system, instruction, context, response, name)
        return self.to_json()
    
    def to_csv(self, dir=None, filename=None, verbose=True, timestamp=True, dir_exist_ok=True, file_exist_ok=False):
        self._logger.to_csv(dir, filename, verbose, timestamp, dir_exist_ok, file_exist_ok)