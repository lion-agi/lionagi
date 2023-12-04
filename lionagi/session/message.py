from datetime import datetime
import json
from ..utils.sys_util import create_id
from ..utils.log_util import DataLogger


class Message:
    """
    A class modeling messages in conversations.

    This class is designed to encapsulate messages exchanged between different roles
    (user, assistant, or system) in a conversation. It includes functionality to process,
    log, and manage messages.

    Attributes:
        role: The role of the message (user, assistant, or system).
        content: The content of the message.
        sender: The sender of the message.
        logger: An instance of DataLogger for logging message information.

    Methods:
        __call__: Process and log a message based on its role.
    """
    def __init__(self) -> None:
        """
        Initialize a Message object with attributes for role, content, sender, and a DataLogger.
        """
        self.role = None
        self.content = None
        self.sender = None
        self.logger = DataLogger()

    def __call__(self, system=None, instruction=None, response=None, context=None, sender=None):
        """
        Process and log a message based on the specified role (system, instruction, or response).

        Args:
            system: The content of the message in the system role.
            instruction: The content of the message in the user role.
            response: The content of the message in the assistant role.
            context: Additional context for the user instruction.
            sender: The sender of the message.
        """
        
        if sum(map(bool, [system, instruction, response])) > 1:
            raise ValueError("Message cannot have more than one role.")
        else:
            if response:
                self.role = "assistant"
                self.sender = sender or "assistant"
                self.content = response['content']
            elif instruction:
                self.role = "user"
                self.sender = sender or "user"
                self.content = {"instruction": instruction}
                if context:
                    self.content.update(context)
            elif system:
                self.role = "system"
                self.sender = sender or "system"
                self.content = system
        out = {
            "role": self.role,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
        
        a = {**{
            "id": create_id(),
            "timestamp": datetime.now().isoformat(),
            "sender": self.sender
        }, **out}
        self.logger(a)
        return out