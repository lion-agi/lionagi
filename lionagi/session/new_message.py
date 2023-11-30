"""
A Message object represents a single message with a unique ID, a timestamp, a role, and content.
"""
import hashlib
import os
import json
from datetime import datetime

class Message:
    def __init__(self) -> None:
        """Initialize a new message with a unique ID and the current timestamp."""
        self.id = self.generate_message_id()
        self.timestamp = datetime.now()
        self.role = None
        self.content = None

    def generate_message_id(self) -> str:
        """
        Generate a pseudorandom hash to be used as the message ID for enhanced privacy.
        Returns a string representing a pseudorandom hash.
        """
        current_time = datetime.now().isoformat().encode('utf-8')
        random_bytes = os.urandom(16)
        return hashlib.sha256(current_time + random_bytes).hexdigest()[:16]

    def __call__(self, system=None, instruction=None, response=None, context=None):
        """
        Create a message with a determined role based on the input provided.
        """
        if sum(map(bool, [system, instruction, response])) > 1:
            raise ValueError("Message cannot have more than one role.")
        else:
            if response:
                self.role = "assistant"
                self.content = response['content']
            elif instruction:
                self.role = "user"
                self.content = {"instruction": instruction}
                if context:
                    self.content.update(context)
            elif system:
                self.role = "system"
                self.content = system
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "role": self.role,
            "data": json.dumps(self.content) if isinstance(self.content, dict) else self.content
        }


class Conversation:
    """
    A Conversation object manages a collection of Message objects and the state of the conversation.
    """
    def __init__(self, system, messages=None) -> None:
        """Initialize a new conversation with a provided system message and optional existing messages."""
        self.messages = messages or []
        self.system = system

    def initiate_conversation(self, system, instruction, context=None):
        """
        Start a new conversation with an initial system message and a user instruction.
        """
        self.messages = []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context)

    def add_messages(self, system=None, instruction=None, context=None, response=None):
        """
        Add a new message to the conversation.
        """
        message = Message()
        message_data = message(system=system, instruction=instruction, response=response, context=context)
        self.messages.append(message_data)

    def change_system(self, system):
        """
        Change the current system description in the conversation.
        """
        if self.messages:
            self.system = system
            system_message = Message()(system=system)
            self.messages[0] = system_message

    def append_last_response(self, response):
        """
        Append the latest assistant response to the conversation messages.
        """
        self.messages.append(Message()(response=response))

    def keep_last_n_exchanges(self, n: int):
        """
        Retain only the last 'n' exchanges (user instructions and assistant responses) in the conversation.
        """
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) if message["role"] == "assistant"
        ]
        if len(response_indices) >= n:
            first_index_to_keep = response_indices[-n] + 1
            self.messages = [self.system] + self.messages[first_index_to_keep:]