
from pathlib import Path
import json
from typing import Any
from dotenv import load_dotenv

from lionagi.schema import DataLogger, Tool
from lionagi.utils import lcall, alcall
from lionagi.configs.oai_configs import oai_schema

from typing import List, Any, Union, Dict, Optional, Tuple
from lionagi.schema.base_node import BaseNode
from datetime import datetime
import json
from typing import Any, Optional, Dict
from lionagi.utils import strip_lower, as_dict, nget, to_readable_dict, lcall, CallDecorator, create_copy, get_flattened_keys

import pandas as pd

import json
from typing import Any, Optional
from lionagi.schema import BaseNode


from ..messages.messages import Message, System, Instruction, Response



class Conversation:

    def __init__(self, dir=None) -> None:
        self.messages = pd.DataFrame(columns=["node_id", "role", "sender", "timestamp" ,"content"])
        self._logger = DataLogger(dir=dir)

    def _create_message(
        self, 
        system: Optional[Any] = None, 
        instruction: Optional[Any] = None, 
        context: Optional[Any] = None, 
        response: Optional[Any] = None, 
        sender: Optional[str] = None
        ) -> Message:
        
        if sum(lcall([system, instruction, response], bool)) != 1:
            raise ValueError("Error: Message must have one and only one role.")
        else:
            if isinstance(any([system, instruction, response]), Message):
                if system:
                    return system
                elif instruction:
                    return instruction
                elif response:
                    return response

            msg = 0
            if response:
                msg = Response(response=response, sender=sender)
            elif instruction:
                msg = Instruction(instruction=instruction, 
                                  context=context, sender=sender)
            elif system:
                msg = System(system=system, sender=sender)
            return msg

    def add_message(
        self, system=None, instruction=None, 
        context=None, response=None, sender=None):
        msg = self._create_message(
            system=system, instruction=instruction, 
            context=context, response=response, sender=sender
        )
        message_dict = msg.to_dict()
        if isinstance(message_dict['content'], dict):
            message_dict['content'] = json.dumps(message_dict['content'])
        message_dict['timestamp'] = datetime.now()
        self.messages.loc[len(self.messages)] = message_dict
    
    @property
    def last_row(self):
        return self.messages.iloc[-1]
    
    @property
    def first_system(self):
        return self.messages[self.messages.role == 'system'].iloc[0]
        
    @property
    def last_response(self):
        return self.get_last_row(role='assistant')
    
    @property
    def last_instruction(self):
        return self.get_last_row(role='user')

    def get_last_n_row(self, sender=None, role=None, n=1):
        if sum(lcall([sender, role], bool)) != 1:
            raise ValueError("Error: can only get last row by one criteria.")
        if sender:
            return self.messages[self.messages.sender == sender].iloc[-n:] if n > 1 else self.messages[self.messages.sender == sender].iloc[-1]
        else:
            return self.messages[self.messages.role == role].iloc[-n:] if n > 1 else self.messages[self.messages.role == role].iloc[-1]

    def get_messages_by(self, node_id=None, role=None, sender=None, timestamp=None ,content=None):
        
        if sum(lcall([node_id, role, sender, timestamp, content], bool)) != 1:
            raise ValueError("Error: can only get DataFrame by one criteria.")
        if node_id:
            return self.messages[self.messages["node_id"] == node_id]
        elif role:
            return self.messages[self.messages["role"] == role]
        elif sender:
            return self.messages[self.messages["sender"] == sender]
        elif timestamp:
            return self.messages[self.messages["timestamp"] == timestamp]
        elif content:
            return self.messages[self.messages["content"] == content]

    def replace_keyword(self, keyword: str, replacement: str, case_sensitive: bool = False) -> None:
        if not case_sensitive:
            self.messages["content"] = self.messages["content"].str.replace(
                keyword, replacement, case=False
            )
        else:
            self.messages["content"] = self.messages["content"].str.replace(
                keyword, replacement
            )

    def search_keyword(self, keyword: str, case_sensitive: bool = False) -> pd.DataFrame:
        if not case_sensitive:
            keyword = keyword.lower()
            return self.messages[
                self.messages["content"].str.lower().str.contains(keyword)
            ]
        return self.messages[self.messages["content"].str.contains(keyword)]

    def remove_from_messages(self, message_id: str) -> bool:
        initial_length = len(self.messages)
        self.messages = self.messages[self.messages["node_id"] != message_id]
        return len(self.messages) < initial_length

    def update_messages_content(self, message_id: str, col: str, value) -> bool:
        index = self.messages.index[self.messages["id_"] == message_id].tolist()
        if index:
            self.messages.at[index[0], col] = value
            return True
        return False

    def info(self, use_sender=False) -> Dict[str, int]:
        messages = self.messages['name'] if use_sender else self.messages['role']
        result = messages.value_counts().to_dict()
        result['total'] = len(self.messages)
        return result

    @property
    def describe(self) -> Dict[str, Any]:
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.messages_info(),
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    def history(
        self, begin_: Optional[datetime] = None, end_: Optional[datetime] = None
    ) -> pd.DataFrame:
        
        if isinstance(begin_, str):
            begin_ = datetime.strptime(begin_, '%Y-%m-%d')
        if isinstance(end_, str):
            end_ = datetime.strptime(end_, '%Y-%m-%d')
        if begin_ and end_:
            return self.messages[
                (self.messages["timestamp"].dt.date >= begin_.date())
                & (self.messages["timestamp"].dt.date <= end_.date())
            ]
        elif begin_:
            return self.messages[(self.messages["timestamp"].dt.date >= begin_.date())]
        elif end_:
            return self.messages[(self.messages["timestamp"].dt.date <= end_.date())]
        return self.messages

    def clone(self) -> 'Conversation':
        cloned = Conversation()
        cloned._logger.set_dir(self._logger.dir)
        cloned.messages = self.messages.copy()
        return cloned

    def merge_conversation(self, other: 'Conversation', update=False) -> None:
        if update:
            self.first_system = other.first_system.copy()
        df = pd.concat([self.messages.copy(), other.messages.copy()], ignore_index=True)
        self.messages = df.drop_duplicates().reset_index(drop=True)

    def rollback(self, steps: int) -> None:
        if steps < 0 or steps > len(self.messages):
            raise ValueError("Steps must be a non-negative integer less than or equal to the number of messages.")
        self.messages = self.messages[:-steps].reset_index(drop=True)

    def reset(self) -> None:
        self.messages = pd.DataFrame(columns=self.messages.columns)

    def to_csv(self, filepath: str, **kwargs) -> None:
        self.messages.to_csv(filepath, **kwargs)

    def from_csv(self, filepath: str, **kwargs) -> None:
        self.messages = pd.read_csv(filepath, **kwargs)

    def to_json(self, filepath: str) -> None:
        self.messages.to_json(
            filepath, orient="records", lines=True, date_format="iso")

    def from_json(self, filepath: str) -> None:
        self.reset()
        self.messages = pd.read_json(filepath, orient="records", lines=True)
    
    def extend(self, messages: pd.DataFrame):
        self.messages = pd.concat([self.messages, messages], ignore_index=True)
        self.messages.drop_duplicates(inplace=True)
        self.messages.reset_index(drop=True, inplace=True)