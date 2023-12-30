from ..schema.base_schema import Message


class Response(Message):
 
    def _create_func_message(self, response, name):
        try:
            tool_count = 0
            func_list = []

            while tool_count < len(response['tool_calls']):
                
                f = lambda i: response['tool_calls'][i]
                f1 = lambda i: f(i)['type']
                f2 = lambda i: f(i)['function']
                f3 = lambda i: (f2(i)['name'], f2(i)['arguments'])
            
                if f1(tool_count) == 'function':
                    _name, _args = f3(tool_count)
                    
                    func_content = {
                        "function": (f"func_{_name}"),            
                        "arguments": _args
                        }
                    
                    func_list.append(func_content)
                tool_count += 1

            self._create_role_message(role_="user",
                                    content=func_list,
                                    content_key="function_list",
                                    name=name or 'func_request')
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
    
    def create_message(self, instruction, context, name):
        self._create_role_message(role_="user",
                                  content=instruction,
                                  content_key="instruction",
                                  name=name)
        if context:
            self.content.update({"context":context})
    
    
class System(Message):

    def create_message(self, system, name):
        self._create_role_message(role_="system",
                                  content=system,
                                  content_key="system",
                                  name=name)
        