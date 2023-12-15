from datetime import datetime
import json
from ..utils.sys_util import create_id, l_call
from ..utils.log_util import DataLogger


class Message:
    """
    A class representing a message in a conversation.

    This class encapsulates messages from users, the assistant, systems, and external tools.

    Attributes:
        role (str): The role of the message, indicating if it's from the user, assistant, system, or tool.
        content: The content of the message, which can be an instruction, response, system setting, or tool information.
        name (str): The name associated with the message, specifying the source (user, assistant, system, or tool).
        metadata (dict): Additional metadata including id, timestamp, and name.
        _logger (DataLogger): An instance of the DataLogger class for logging message details.

    Methods:
        create_message(system, instruction, context, response, tool, name):
            Create a message based on the provided information.

        to_json() -> dict:
            Convert the message to a JSON format.

        __call__(system, instruction, context, response, name, tool) -> dict:
            Create and return a message in JSON format.

        to_csv(dir, filename, verbose, timestamp, dir_exist_ok, file_exist_ok):
            Save the message to a CSV file.
    """
    def __init__(self) -> None:
        """
        Initialize a Message object.
        """
        self.role = None
        self.content = None
        self.name = None
        self.metadata = None
        self._logger = DataLogger()
    
    def create_message(self, system=None, instruction=None, context=None, response=None, name=None):

        """
        Create a message based on the provided information.

        Parameters:
            system (str): The system setting for the message. Default is None.
            instruction (str): The instruction content for the message. Default is None.
            context (dict): Additional context for the message. Default is None.
            response (dict): The response content for the message. Default is None.
            tool (dict): The tool information for the message. Default is None.
            name (str): The name associated with the message. Default is None.
        """
        if sum(l_call([system, instruction, response], bool)) > 1:
            raise ValueError("Error: Message cannot have more than one role.")
        
        else: 
            if response:
                self.role = "assistant"
                try:
                    response = response["message"]
                    if str(response['content']) == "None":
                        try:
                            if response['tool_calls'][0]['type'] == 'function':
                                self.name = name or ("func_" + response['tool_calls'][0]['function']['name'])
                                content = response['tool_calls'][0]['function']['arguments']
                                self.content = {"function":self.name, "arguments": content}
                        except:
                            raise ValueError("Response message must be one of regular response or function calling")
                    else:
                        self.content = response['content']
                        self.name = name or "assistant"
                except:
                    self.name = name or "func_call"
                    self.content = {"function call result": response}
                
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
        """
        Convert the message to a JSON format.

        Returns:
        - dict: The message in JSON format.
        """
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
        
    def __call__(self, system=None, instruction=None, context=None, 
                 response=None, name=None):
        """
        Create and return a message in JSON format.

        Parameters:
            system (str): The system setting for the message. Default is None.
            instruction (str): The instruction content for the message. Default is None.
            context (dict): Additional context for the message. Default is None.
            response (dict): The response content for the message. Default is None.
            name (str): The name associated with the message. Default is None.
            tool (dict): The tool information for the message. Default is None.

        Returns:
            dict: The message in JSON format.
        """
        self.create_message(system=system, instruction=instruction, 
                            context=context, response=response, name=name)
        return self.to_json()
    
    def to_csv(self, dir=None, filename=None, verbose=True, timestamp=True, dir_exist_ok=True, file_exist_ok=False):
        """
        Save the message to a CSV file.

        Parameters:
            dir (str): The directory path for saving the CSV file. Default is None.
            filename (str): The filename for the CSV file. Default is None.
            verbose (bool): Whether to include verbose information in the CSV. Default is True.
            timestamp (bool): Whether to include timestamps in the CSV. Default is True.
            dir_exist_ok (bool): Whether to allow the directory to exist. Default is True.
            file_exist_ok (bool): Whether to allow the file to exist. Default is False.
        """
        self._logger.to_csv(dir, filename, verbose, timestamp, dir_exist_ok, file_exist_ok)