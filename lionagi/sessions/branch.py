from ..messages.messenger import Messenger
from ..tools.tool_manager import ToolManager
from ..core.conversation import Conversation


class Branch:
    
    # instruction set is an object
    def __init__(self, system=None, instruction_set=None, messages=None) -> None:
        self.system = system or instruction_set.system or "A helpful assistant"
        self.instruction_set = Conversation(instruction_set)
        self.conversation = Conversation(messages)
        self.msgr = Messenger()
        self.tool_manager = ToolManager()
    
    def handle_instruction():
        ...
        
    def send_report():
        ...
        
    def handle_error():
        ...
    
    def start():
        ...
        
    def close():
        ...
    
    

class Session:
    
    def create_branch():
        ...
        
    def start_branch():
        ...
        
    def pause_branch():
        ...
    
    def central_log():
        ...
    
    def end_branch():
        ...
    
    
    
    ...