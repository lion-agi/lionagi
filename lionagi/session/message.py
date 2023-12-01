from datetime import datetime
import json
from ..utils.log_util import DataLogger


class Message:
    def __init__(self) -> None:
        self.timestamp = datetime.now()
        self.role = None
        self.content = None
        self.sender = None
        self.logger = DataLogger()

    def __call__(self, system=None, instruction=None, response=None, context=None, sender=None):
        
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
        
        a = {**out, **{
            "id": self.logger.generate_id(),
            "timestamp": self.timestamp.isoformat(),
            "sender": self.sender
        }}
        self.logger(a)
        return out