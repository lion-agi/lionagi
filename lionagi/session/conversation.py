"""   
Copyright 2023 HaiyangLi <ocean@lionagi.ai>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from .message import massenger

class Conversation:
    """
    Manages a conversation consisting of multiple messages.

    Attributes:
        response_counts (int): A class-level counter for responses.
        messages (list): A list of messages in the conversation.
        system (str): System-related message.
        responses (list): A list to store responses.
    Methods:
        initiate_conversation: Initializes a new conversation.
        add_messages: Adds a new message to the conversation.
        change_system: Changes the system message.
        append_last_response: Adds the last response to the list of messages.
    """

    response_counts = 0

    def __init__(self, system, messages=[]) -> None:
        self.messages = messages
        self.system = system
        self.responses = []

    def initiate_conversation(self, system, instruction, context=None):
        """
        Initializes a new conversation by setting the initial system and instruction messages.

        Args:
            system (str): The initial system message.
            instruction (str): The initial instruction from the user.
            context (dict, optional): Additional context for the instruction. Defaults to None.
        """
        self.messages = []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context)

    def add_messages(
        self, system=None, instruction=None, context=None, response=None
    ):
        """
        Adds a new message to the conversation.

        Args:
            system (str, optional): System-related message. Defaults to None.
            instruction (str, optional): User's instruction. Defaults to None.
            context (dict, optional): Additional context for the instruction. Defaults to None.
            response (dict, optional): Assistant's response. Defaults to None.
        """
        message = massenger(
            system=system, response=response, instruction=instruction, context=context
        )
        self.messages.append(message)

    def change_system(self, system):
        """
        Changes the initial system message.

        Args:
            system (str): The new system message.
        """
        self.system = system
        self.messages[0] = massenger(system=system)

    def append_last_response(self):
        """
        Appends the last response to the list of messages.
        """
        self.add_messages(response=self.responses[-1])
        
    def keep_last_n_exchanges(self, n: int, system=None) -> None:
        """
        Truncates front messages to only include the last n exchanges between the user and the assistant.
        Always keeps the initial system message.

        Args:
            n (int): Number of exchanges to retain. One exchange consists of one instruction and one response.
            system (str): The new system message. Defaults to the initial system message.

        """
        # Keep the system message
        system = system or self.messages[0]
        
        # Count how many assistant's responses are in the conversation
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) if message["role"] == "assistant"
        ]
        
        # Calculate the index from where to start keeping the messages
        if len(response_indices) >= n:
            first_index_to_keep = response_indices[-n]  # This index is based on slicing from 1
            first_index_to_keep += 1  # Adjust index to include system message
            
            # Truncate messages but keep the system message
            self.messages = [system] + self.messages[first_index_to_keep:]
        else:
            # If there are fewer than n exchanges, do nothing
            pass