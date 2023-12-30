import json
from ..utils.sys_utils import l_call
from ..schema import BaseNode


class Message(BaseNode):
    role : str
    name : str
    



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



    def _create_role_message(self, role_, content, content_key, name):
        self.role = role_
        self.content = {content_key: content}
        self.name = name or role_




class Response(Message):

            
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

    def create_message(self, response, name):
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


 
class Instruction(Message):
    
    def create_message(self, instruction, name):
        self._create_role_message(role_="user",
                                  content=instruction,
                                  content_key="instruction",
                                  name=name)
    
    
class System(Message):

    def create_message(self, system, name):
        self._create_role_message(role_="system",
                                  content=system,
                                  content_key="system",
                                  name=name)




    
class Messenger:
    
    def __init__(self) -> None:
        pass
    
    
    @classmethod
    def __call__(cls, message=None):
        return message._create_role_message()
    
    
    def create_message(self, system=None, 
                       instruction=None, 
                       context=None, 
                       response=None, 
                       name=None):
        
        if sum(l_call([system, instruction, response], bool)) > 1:
            raise ValueError("Error: Message cannot have more than one role.")
        
        else: 
            if response:
                message = 
                
                
                self._create_assistant_message(response=response, 
                                               name=name)
            elif instruction:
                self._create_user_message(instruction=instruction, 
                                          name=name, 
                                          context=context)
            elif system:
                self._create_sys_message(system=system, 
                                         name=name)