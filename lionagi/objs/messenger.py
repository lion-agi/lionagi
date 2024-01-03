# from typing import Optional, Any, Union, Dict, Tuple

# from lionagi.utils.call_util import lcall
# from lionagi.schema.data_logger import DataLogger
# from lionagi.core.messages import Message, Response, Instruction, System


# class Messenger:
#     """
#     Messenger handles the creation, logging, and exporting of messages.

#     This class is responsible for creating various types of messages (system, instruction, response),
#     logging them, and optionally exporting the log to a CSV file.

#     Attributes:
#         _logger (DataLogger): An instance of DataLogger to manage message logging.
    
#     Methods:
#         set_dir: Sets the directory for the DataLogger to save CSV files.
        
#         set_log: Sets the log object for the DataLogger.
        
#         log_message: Logs a message in JSON format.
        
#         to_csv: Exports logged messages to a CSV file.
        
#         _create_message: Internal method to create a specific type of message.
        
#         create_message: Public interface to create messages, log them, and optionally return them in different formats.
#     """
    
#     def __init__(self) -> None:
#         """
#         Initializes the Messenger with a DataLogger instance.
#         """
#         self._logger = DataLogger()
        
#     def set_dir(self, dir: str) -> None:
#         """
#         Sets the directory where the DataLogger will save CSV files.

#         Parameters:
#             dir (str): The directory path to set for the DataLogger.
#         """
#         self._logger.dir = dir
    
#     def set_log(self, log) -> None:
#         """
#         Sets the log object for the DataLogger.

#         Parameters:
#             log: The log object to be used by the DataLogger.
#         """
#         self._logger.log = log
        
#     def log_message(self, msg: Message) -> None:
#         """
#         Logs a message in JSON format using the DataLogger.

#         Parameters:
#             msg (Message): The message object to be logged.
#         """
#         self._logger(msg.to_json())
        
#     def to_csv(self, **kwargs) -> None:
#         """
#         Exports the logged messages to a CSV file.

#         Parameters:
#             **kwargs: Additional keyword arguments to be passed to the DataLogger's to_csv method.
#         """
#         self._logger.to_csv(**kwargs)
        
#     def _create_message(self, 
#                         system: Optional[Any] = None, 
#                         instruction: Optional[Any] = None, 
#                         context: Optional[Any] = None, 
#                         response: Optional[Any] = None, 
#                         name: Optional[str] = None) -> Message:
#         """
#         Creates a specific type of message based on the provided parameters.

#         Parameters:
#             system (Optional[Any]): System message content.
            
#             instruction (Optional[Any]): Instruction message content.
            
#             context (Optional[Any]): Context for the instruction message.
            
#             response (Optional[Any]): Response message content.
            
#             name (Optional[str]): Name associated with the message.

#         Returns:
#             Message: The created message object of type Response, Instruction, or System.

#         Raises:
#             ValueError: If more than one or none of the message content parameters (system, instruction, response) are provided.
#         """
        
#         if sum(lcall([system, instruction, response], bool)) != 1:
#             raise ValueError("Error: Message must have one and only one role.")
        
#         else:
#             msg = 0
            
#             if response:
#                 msg = Response()
#                 msg.create_message(response=response, 
#                                    name=name,)
#             elif instruction:
#                 msg = Instruction()
#                 msg.create_message(instruction=instruction, 
#                                    context=context, 
#                                    name=name,)
#             elif system:
#                 msg = System()
#                 msg.create_message(system=system,
#                                    name=name,)
#             return msg
    
#     def create_message(self, 
#                        system: Optional[Any] = None, 
#                        instruction: Optional[Any] = None, 
#                        context: Optional[Any] = None, 
#                        response: Optional[Any] = None, 
#                        name: Optional[str] = None,
#                        obj: bool = False,
#                        log_: bool = True) -> Union[Message, Tuple[Message, Dict]]:
#         """
#         Creates and optionally logs a message, returning it in different formats based on parameters.

#         Parameters:
#             system (Optional[Any]): System message content.
            
#             instruction (Optional[Any]): Instruction message content.
            
#             context (Optional[Any]): Context for the instruction message.
            
#             response (Optional[Any]): Response message content.
            
#             name (Optional[str]): Name associated with the message.
            
#             obj (bool): If True, returns the Message object and its dictionary representation. Defaults to False.
            
#             log_ (bool): If True, logs the created message. Defaults to True.

#         Returns:
#             Union[Message, Tuple[Message, Dict]]: The created message in the specified format.
#         """
        
#         msg = self._create_message(system=system, 
#                                   instruction=instruction, 
#                                   context=context, 
#                                   response=response, 
#                                   name=name)
#         if log_:
#             self.log_message(msg)
#         if obj:
#             return (msg, msg._to_message())
#         else:
#             return msg._to_message()
    