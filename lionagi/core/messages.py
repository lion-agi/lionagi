import json
from ..utils import l_call
from ..schema import DataLogger, MessageNode


class Message(MessageNode):
    _logger = DataLogger()
    
    def _process_system(self, system, name):
        self._set_value(role="system", content=system, name=name)
    
    def _process_instruction(self, instruction, context, name):
        self._set_value(role="user", content={"instruction": instruction}, name=name)
        if context:
            self.content.update({"context": context})

    def _process_response(self, response, name):
        self.role = "assistant"
        try:
            response_message = response.get("message", {})
            content = response_message.get('content')
            if str(content) == "None":
                self._handle_function_calls(response_message, name)
            else:
                self.content = content
                self.name = name or "assistant"
        except:
            self.name = name or "func_call"
            self.content = response            
            
    def _create_message(self, system=None, instruction=None, context=None, response=None, name=None):
        if sum(l_call([system, instruction, response], bool)) > 1:
            raise ValueError("Error: Message cannot have more than one role.")
        
        if system:
            self._process_system(system=system, name=name)
        elif response:
            self._process_response(response=response, name=name)
        elif instruction:
            self._process_instruction(instruction=instruction, context=context, name=name)
        
    def _handle_function_calls(self, response_message, name):
        try:
            function_calls = response_message.get('tool_calls', [])
            func_list = self._extract_functions(function_calls)
            self.content = {'function_list': func_list}
            self.name = name or "func_request"
        except Exception as e:
            raise ValueError(f"Invalid function call structure: {e}")

    def _set_value(self, role, content=None, name=None):        
        self.role = role
        self.name = name or role
        self.content = content

    def _to_msg(self):
        out = {
            "role": self.role, 
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
        self.add_meta({"name": self.name})
        self._logger(self.to_dict())
        return out
        
    def create_message(self, system=None, instruction=None, context=None, 
                 response=None, name=None):
        self._create_message(system=system, instruction=instruction, 
                            context=context, response=response, name=name)
        
        return self._to_msg()
    
    def to_csv(self, dir=None, filename=None, verbose=True, timestamp=True, dir_exist_ok=True, file_exist_ok=False):
        self._logger.to_csv(dir, filename, verbose, timestamp, dir_exist_ok, file_exist_ok)
        