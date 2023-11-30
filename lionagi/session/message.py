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

import json

class Message:

    def __init__(self, role=None, content=None) -> None:
        self.role = role
        self.content = content

    def _create_message(
        self, system=None, response=None, instruction=None, context=None):
        """
        Internal method to set the `role` and `content` attributes based on the provided parameters.

        Args:
            system (str, optional): System-related message. Defaults to None.
            response (dict, optional): Assistant's response. Defaults to None.
            instruction (str, optional): User's instruction. Defaults to None.
            context (dict, optional): Additional context for the instruction. Defaults to None.

        Raises:
            ValueError: If more than one role is provided for a single message.
        """
        
        if (system and (response or instruction)) or (response and instruction):
            raise ValueError("Error: Message cannot have more than one role.")
        else:
            if response:
                self.role = "assistant"
                self.content = response['content']
            elif instruction:
                self.role = "user"
                self.content = {"instruction": instruction}
                if context:
                    for k, v in context.items():
                        self.content[k] = v
            elif system:
                self.role = "system"
                self.content = system

    def __call__(self, system=None, response=None, instruction=None, context=None):
        """
        Converts the Message object to a dictionary representation when the object is called.

        Args:
            system (str, optional): System-related message. Defaults to None.
            response (dict, optional): Assistant's response. Defaults to None.
            instruction (str, optional): User's instruction. Defaults to None.
            context (dict, optional): Additional context for the instruction. Defaults to None.

        Returns:
            dict: A dictionary representation of the Message object.
        """

        self._create_message(
            system=system, response=response, instruction=instruction, context=context
        )
        if self.role == "assistant":
            return {"role": self.role, "content": self.content}
        else:
            return {"role": self.role, "content": json.dumps(self.content)}

massenger = Message()