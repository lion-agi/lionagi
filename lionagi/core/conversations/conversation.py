from typing import List, Any

from lionagi.schema.base_node import BaseNode
from lionagi.messages import Message, Response
from lionagi.objs.messenger import Messenger


class Conversation(BaseNode):

    response_counts : int = 0
    messages: List[Message] = []
    msgr : Any = Messenger()
    responses: List[Response] = []

    def initiate_conversation(
        self, system=None, instruction=None, 
        context=None, name=None
    ):
        self.messages, self.responses = [], []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context, name=name)

    def add_messages(
        self, system=None, instruction=None, 
        context=None, response=None, name=None
    ):
        msg = self.msgr.create_message(
            system=system, instruction=instruction, 
            context=context, response=response, name=name
        )
        self.messages.append(msg)

    def change_system(self, system):
        self.messages[0] = self.msgr.create_message(system=system)

    def keep_last_n_exchanges(self, n: int):
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) 
            if message.role == "user"
        ]
        if len(response_indices) >= n:
            first_index_to_keep = response_indices[-n] + 1
            self.messages = [self.system] + self.messages[first_index_to_keep:]
    
    def last_messages(self, n=1):
        try:
            return self.messages[-n:]
        except:
            raise ValueError(f"Conversation has less than {n} messages.")
    
    def set_messages(self, messages):
        self.messages = messages

    