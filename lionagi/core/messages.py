import json
from ..utils.sys_utils import l_call
from ..schema.message_nodes import MessageNode


class Message(MessageNode):
   
    def _create_sys_message(self, system, name):
        self.role = "system"
        self.content = system
        self.name = name or "system"
    
    def _create_user_message(self, instruction, name, context):
        self.role = "user"
        self.content = {"instruction": instruction}
        
        if context:
            self.content.update({"context": context})
            
        self.name = name or "user"
    
    def _create_func_message(self, response, name):
        try:
            tool_count = 0
            func_list = []
            
            while tool_count < len(response['tool_calls']):
                if response['tool_calls'][tool_count]['type'] == 'function':
                    
                    func_content = {
                        "function": 
                            ("func_" + response['tool_calls'][tool_count]['function']['name']),            
                            
                        "arguments": 
                            response['tool_calls'][tool_count]['function']['arguments']
                        }
                    
                    func_list.append(func_content)
                tool_count += 1

            self.name = name or "func_request"
            self.content = {'function_list': func_list}
            
        except:
            raise ValueError("Response message must be one of regular response or function calling")

    def _create_assistant_message(self, response, name):
        self.role = "assistant"
        
        try:
            response = response["message"]
            if str(response['content']) == "None":
                self._create_func_message(response=response, 
                                          name=name)
            else:
                self.content = response['content']
                self.name = name or "assistant"
                
        except:
            self.name = name or "func_call"
            self.content = response

    def create_message(self, system=None, 
                       instruction=None, 
                       context=None, 
                       response=None, 
                       name=None):
        
        if sum(l_call([system, instruction, response], bool)) > 1:
            raise ValueError("Error: Message cannot have more than one role.")
        
        else: 
            if response:
                self._create_assistant_message(response=response, 
                                               name=name)
            elif instruction:
                self._create_user_message(instruction=instruction, 
                                          name=name, 
                                          context=context)
            elif system:
                self._create_sys_message(system=system, 
                                         name=name)

    def _output(self):
        out = {
            "role": self.role,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
        
        self._logger({self.to_json()})
        return out

    def __call__(self, system=None, instruction=None, context=None, 
                 response=None, name=None):
        self.create_message(system=system, instruction=instruction, 
                            context=context, response=response, name=name)
        return self._output()
    