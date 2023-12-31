from ..schema.base_schema import Message


class Response(Message):
    """
    Response class for creating a response message type.

    This class is used to create a response message which can be a regular response or a function calling response.

    Methods:
        _create_func_message: Creates a function calling message.
        create_message: Creates a regular response message or a function calling message based on the input.
    """    
 
    def _create_func_message(self, response, name):
        """
        Creates a function calling message.

        Parameters:
            response (dict): The response containing the tool calls.
            name (str): The name associated with the message.

        Raises:
            ValueError: If the response does not follow the expected structure for function calling.
        """        
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
        """
        Creates a response message.

        Based on the response content, it either creates a regular response message or a function calling message.

        Parameters:
            response (dict): The response data.
            name (Optional[str]): The name associated with the message. Defaults to "assistant" or "func_call".
        """        
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
    """
    Instruction class for creating an instruction message type.

    This class is used to create an instruction message which includes the instruction and optionally the context.

    Methods:
        create_message: Creates an instruction message with the provided instruction and context.
    """    
    
    def create_message(self, instruction, context, name):
        """
        Creates an instruction message.

        Parameters:
            instruction (Any): The instruction content.
            context (Optional[Any]): Additional context for the instruction. Defaults to None.
            name (Optional[str]): The name associated with the message. Defaults to "user".

        Note:
            If context is provided, it is included in the message content.
        """        
        self._create_role_message(role_="user",
                                  content=instruction,
                                  content_key="instruction",
                                  name=name)
        if context:
            self.content.update({"context":context})
    
    
class System(Message):
    """
    System class for creating a system message type.

    This class is used to create a system message which includes system-specific content.

    Methods:
        create_message: Creates a system message with the provided system content.
    """    

    def create_message(self, system, name):
        """
        Creates a system message.

        Parameters:
            system (Any): The system content.
            name (Optional[str]): The name associated with the message. Defaults to "system".
        """        
        self._create_role_message(role_="system",
                                  content=system,
                                  content_key="system",
                                  name=name)
        