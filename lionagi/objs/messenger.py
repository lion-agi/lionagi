from collections import deque
from typing import Optional, Any, Union, Dict, Tuple

from lionagi.utils.call_util import lcall
from lionagi.schema.data_logger import DataLogger
from lionagi.messages import Message, Response, Instruction, System


class Messenger:
    
    def __init__(self) -> None:
        self._logger = DataLogger()
        
    def set_dir(self, dir: str) -> None:
        self._logger.dir = dir
    
    def set_log(self, log) -> None:
        self._logger.log = log
        
    def log_message(self, msg: Message) -> None:
        self._logger(msg.to_json())
        
    def to_csv(self, **kwargs) -> None:
        self._logger.to_csv(**kwargs)
    
    def clear_log(self):
        self._logger.log = deque()
    
    def _create_message(
        self, 
        system: Optional[Any] = None, 
        instruction: Optional[Any] = None, 
        context: Optional[Any] = None, 
        response: Optional[Any] = None, 
        name: Optional[str] = None
        ) -> Message:
        
        if sum(lcall([system, instruction, response], bool)) != 1:
            raise ValueError("Error: Message must have one and only one role.")
        
        else:
            msg = 0
            
            if response:
                msg = Response()
                msg._create_message(
                    response=response, name=name,
                    )
            elif instruction:
                msg = Instruction()
                msg._create_message(
                    instruction=instruction, context=context, 
                    name=name,
                    )
            elif system:
                msg = System()
                msg._create_message(
                    system=system, name=name,
                    )
            return msg
    
    def create_message(
        self, 
        system: Optional[Any] = None, 
        instruction: Optional[Any] = None, 
        context: Optional[Any] = None, 
        response: Optional[Any] = None, 
        name: Optional[str] = None, 
        obj: bool = True, 
        log_: bool = True
        ) -> Union[Message, Tuple[Message, Dict]]:
        
        msg = self._create_message(
            system=system, 
            instruction=instruction, 
            context=context, 
            response=response, 
            name=name
            )
        
        if log_:
            self.log_message(msg)
        if obj:
            return msg
    