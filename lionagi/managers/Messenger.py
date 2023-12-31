from lionagi.utils.call_utils import l_call
from lionagi.schema.base_schema import DataLogger
from lionagi.core.messages import Message, Response, Instruction, System


class Messenger:
    
    def __init__(self) -> None:
        self._logger = DataLogger()
        
    def set_dir(self, dir):
        self._logger.dir = dir
    
    def set_log(self, log):
        self._logger.log = log
        
    def log_message(self, msg):
        self._logger(msg.to_json())
        
    def to_csv(self, **kwargs):
        self._logger.to_csv(**kwargs)
        
    def _create_message(self, 
                        system=None, 
                        instruction=None, 
                        context=None, 
                        response=None, 
                        name=None,
                        ) -> Message:
        
        if sum(l_call([system, instruction, response], bool)) != 1:
            raise ValueError("Error: Message must have one and only one role.")
        
        else:
            msg = 0
            
            if response:
                msg = Response()
                msg.create_message(response=response, 
                                   name=name,)
            elif instruction:
                msg = Instruction()
                msg.create_message(instruction=instruction, 
                                   context=context, 
                                   name=name,)
            elif system:
                msg = System()
                msg.create_message(system=system,
                                   name=name,)
            return msg
    
    def create_message(self, 
                       system=None, 
                       instruction=None, 
                       context=None, 
                       response=None, 
                       name=None,
                       obj=False,
                       log_=True,
                       ):
        
        msg = self.create_message(system=system, 
                                  instruction=instruction, 
                                  context=context, 
                                  response=response, 
                                  name=name)
        if log_:
            self.log_message(msg)
        if obj:
            return (msg, msg._to_message())
        else:
            return msg._to_message()
    