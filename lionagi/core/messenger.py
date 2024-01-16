from typing import Optional, Any, Union, Dict, Tuple

from ..utils.call_util import lcall
from ..schema.data_logger import DataLogger
from .messages import Message, Response, Instruction, System


class Messenger:
    
    def __init__(self) -> None:
        self._logger = DataLogger()
        
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
                msg._create_message(response=response, name=name)
                
            elif instruction:
                msg = Instruction()
                msg._create_message(instruction=instruction, context=context, name=name)
                
            elif system:
                msg = System()
                msg._create_message(system=system, name=name)
                
            return msg
    
    def create_message(
        self, 
        system: Optional[Any] = None, 
        instruction: Optional[Any] = None, 
        context: Optional[Any] = None, 
        response: Optional[Any] = None, 
        name: Optional[str] = None, 
        ) -> Union[Message, Tuple[Message, Dict]]:
        
        msg = self._create_message(
            system=system, 
            instruction=instruction, 
            context=context, 
            response=response, 
            name=name
            )
    
        return msg


    # def add_new_message(self, message: Message) -> None:
    #     """Adds a new message and performs additional updates if necessary."""
    #     self.add_message(message)
    #     # Additional logic (e.g., notifications) can be added here

    # def delete_message(self, index: Optional[int] = None, range_to_delete: Optional[Tuple[int, int]] = None) -> None:
    #     """Deletes a message or range of messages and handles any cleanup."""
    #     self.delete_messages(index, range_to_delete)
    #     # Additional cleanup can be done here

    # def find_and_replace(self, keyword: str, replacement: str, case_sensitive: bool = False) -> None:
    #     """Finds and replaces a keyword in all messages."""
    #     self.replace_keyword(keyword, replacement, case_sensitive)
    #     # Post-replacement logic can be implemented here

    # def archive(self, archive_path: str) -> None:
    #     """Archives the entire."""
    #     self.export(archive_path)
    #     # Additional archival steps can be taken here

    # def load_archived(self, archive_path: str) -> None:
    #     """Loads an archived."""
    #     self.import(archive_path)
    #     # Post-loading logic can be implemented here

    # def summarize_and_report(self) -> Dict[str, Any]:
    #     """Generates a summary and detailed report of the."""
    #     summary = self.summarize()
    #     detailed_report = self.generate_report()
    #     # Combine or post-process the summary and report as needed
    #     return {
    #         "summary": summary,
    #         "detailed_report": detailed_report
    #     }

    # def mark_important_messages(self, flags: Set[str]) -> None:
    #     """Marks messages that are deemed important based on given flags."""
    #     for index, message in enumerate(self.messages):
    #         if any(flag in message.flags for flag in flags):
    #             self.mark_message(index, "important")
    #     # Additional flagging logic can be added here

    # def retrieve_importants(self) -> List[Message]:
    #     """Retrieves important messages from the."""
    #     return self.retrieve_marked_messages("important")