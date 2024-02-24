from typing import Any, Optional

from lionagi.core.session.message import BaseMessage
from lionagi.util import strip_lower, to_dict, nget
from lionagi.core.session.message.schema import (MessageField, MessageContentKey, MessageRoleType,
                                                 MessageSenderType)


class Instruction(BaseMessage):
    """
    Represents an instruction message, typically used to convey actions or commands.

    This class is intended for messages that carry instructions from users or automated
    systems, possibly including a context for the instruction.

    Args:
        instruction (Any): The main instruction or command this message is carrying.
        context (Optional[Any], optional): Additional context or parameters for the instruction.
        sender (Optional[str], optional): The identifier for the entity sending the instruction.
            Defaults to the role type converted to string if not specified.

    Attributes are inherited from `BaseMessage`.
    """

    def __init__(self, instruction: Any, context=None, sender: Optional[str] = None):
        super().__init__(
            role=MessageRoleType.USER.value,
            sender=sender or MessageSenderType.USER.value,
            content={MessageContentKey.INSTRUCTION.value: instruction}
        )
        if context:
            self.content.update({'context': context})


class System(BaseMessage):
    """
    Represents a system message, typically used to convey system-level information or status.

    This class is intended for messages that originate from or are about the system's internal
    processes, configurations, or states.

    Args:
        system (Any): The main content or information this message is carrying about the system.
        sender (Optional[str], optional): The identifier for the entity sending the system message.
            Defaults to the role type converted to string if not specified.

    Attributes are inherited from `BaseMessage`.
    """

    def __init__(self, system: Any, sender: Optional[str] = None):
        super().__init__(
            role=MessageRoleType.SYSTEM.value,
            sender=sender or MessageSenderType.SYSTEM.value,
            content={MessageContentKey.SYSTEM.value: system}
        )


class Response(BaseMessage):

    def __init__(self, response: Any, sender: Optional[str] = None) -> None:
        content_key = ''
        try:
            response = response["message"]
            if strip_lower(response[MessageField.CONTENT.value]) == "none":
                content_ = self._handle_action_request(response)
                sender = sender or MessageSenderType.ACTION_REQUEST
                content_key = content_key or "action_list"

            else:
                try:
                    if 'tool_uses' in to_dict(response['content']):
                        content_ = to_dict(response['content'])['tool_uses']
                        content_key = content_key or "action_list"
                        sender = sender or MessageSenderType.ACTION_REQUEST
                    elif 'response' in to_dict(response['content']):
                        sender = sender or "assistant"
                        content_key = content_key or "response"
                        content_ = to_dict(response['content'])['response']
                    elif 'action_list' in to_dict(response['content']):
                        sender = sender or MessageSenderType.ACTION_REQUEST
                        content_key = content_key or "action_list"
                        content_ = to_dict(response['content'])['action_list']
                    else:
                        content_ = response['content']
                        content_key = content_key or "response"
                        sender = sender or "assistant"
                except:
                    content_ = response['content']
                    content_key = content_key or "response"
                    sender = sender or "assistant"

        except:
            sender = sender or "action_response"
            content_ = response
            content_key = content_key or "action_response"

        super().__init__(
            role=MessageRoleType.ASSISTANT.value, sender=sender, content={content_key:
                                                                         content_}
        )

    @staticmethod
    def _handle_action_request(response):
        try:
            tool_count = 0
            func_list = []
            while tool_count < len(response['tool_calls']):
                _path = ['tool_calls', tool_count, 'type']

                if nget(response, _path) == 'function':
                    _path1 = ['tool_calls', tool_count, 'function', 'name']
                    _path2 = ['tool_calls', tool_count, 'function', 'arguments']

                    func_content = {
                        "action": ("action_" + nget(response, _path1)),
                        "arguments": nget(response, _path2)
                    }
                    func_list.append(func_content)
                tool_count += 1
            return func_list
        except:
            raise ValueError(
                "Response message must be one of regular response or function calling"
            )
