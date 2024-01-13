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

# filename: conversations.py
from typing import List, Any, Optional
from lionagi.schema.base_node import BaseNode
from lionagi.messages import Message, Response
from lionagi.objs.messenger import Messenger

class Conversation(BaseNode):
    response_counts: int = 0
    messages: List[Message] = []
    msgr: Any = Messenger()
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

    # New features implementation
    def total_messages(self):
        return len(self.messages)

    def search_messages(self, keyword: str):
        return [msg for msg in self.messages if keyword in msg.content]

    def tag_message(self, index: int, tag: str):
        if index < len(self.messages):
            self.messages[index].tags.append(tag)

    def get_messages_by_tag(self, tag: str):
        return [msg for msg in self.messages if tag in getattr(msg, 'tags', [])]

    def summarize_conversation(self):
        # Placeholder for summary generation logic
        return "Summary of the conversation."

    def export_conversation(self, filename: str):
        with open(filename, 'w') as file:
            for msg in self.messages:
                file.write(f"{msg}\n")

    def import_conversation(self, filename: str):
        with open(filename, 'r') as file:
            self.messages = [self.msgr.parse_message(line.strip()) for line in file]

    def rate_conversation(self, rating: int):
        self.metadata['rating'] = rating

    def get_last_response(self):
        for msg in reversed(self.messages):
            if isinstance(msg, Response):
                return msg
        return None

    def delete_message(self, index: int):
        if index < len(self.messages):
            del self.messages[index]