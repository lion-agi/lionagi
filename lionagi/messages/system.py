from typing import Any, List, Optional
from .message import Message

class System(Message):
    system_status: Optional[str] = None

    system_logs: List[str] = []

    def _create_message(self, system: Any, name: Optional[str] = None) -> None:
        super().__call__(
            role_="system", 
            content_key="system", 
            content=system, 
            name=name
        )

    def set_system_status(self, status: str):
        self.system_status = status
    
    def get_system_status(self):
        return self.system_status
    
    def log_event(self, event: str):
        self.system_logs.append(event)
    
    def get_system_logs(self):
        return self.system_logs
    
    def clear_system_logs(self):
        self.system_logs = []
        