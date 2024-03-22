from enum import Enum

from lionagi.libs import nested, convert
from ..schema import DataNode

_message_fields = ["node_id", "timestamp", "role", "sender", "recipient", "content"]


# ToDo: actually implement the new message classes


class BranchColumns(list[str], Enum):
    COLUMNS = _message_fields


class MessageField(str, Enum):
    NODE_ID = "node_id"
    TIMESTAMP = "timestamp"
    ROLE = "role"
    SENDER = "sender"
    RECIPIENT = "recipient"
    CONTENT = "content"
    METADATA = "metadata"
    RELATION = "relation"


class MessageRoleType(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageContentKey(str, Enum):
    INSTRUCTION = "instruction"
    CONTEXT = "context"
    SYSTEM = "system_info"
    ACTION_REQUEST = "action_request"
    ACTION_RESPONSE = "action_response"
    RESPONSE = "response"


class MessageType(dict, Enum):
    SYSTEM = (
        {
            MessageField.ROLE.value: MessageRoleType.SYSTEM.value,
            MessageField.SENDER.value: MessageRoleType.SYSTEM.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.SYSTEM.value,
        },
    )

    INSTRUCTION = (
        {
            MessageField.ROLE.value: MessageRoleType.USER.value,
            MessageField.SENDER.value: MessageRoleType.USER.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.INSTRUCTION.value,
        },
    )

    CONTEXT = (
        {
            MessageField.ROLE.value: MessageRoleType.USER.value,
            MessageField.SENDER.value: MessageRoleType.USER.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.CONTEXT.value,
        },
    )

    ACTION_REQUEST = (
        {
            MessageField.ROLE.value: MessageRoleType.ASSISTANT.value,
            MessageField.SENDER.value: MessageRoleType.ASSISTANT.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.ACTION_REQUEST.value,
        },
    )

    ACTION_RESPONSE = (
        {
            MessageField.ROLE.value: MessageRoleType.ASSISTANT.value,
            MessageField.SENDER.value: MessageRoleType.ASSISTANT.value,
            MessageField.RECIPIENT.value: "null",
            "content_key": MessageContentKey.ACTION_RESPONSE.value,
        },
    )

    RESPONSE = {
        MessageField.ROLE.value: MessageRoleType.ASSISTANT.value,
        MessageField.SENDER.value: MessageRoleType.ASSISTANT.value,
        MessageField.RECIPIENT.value: "null",
        "content_key": MessageContentKey.RESPONSE.value,
    }


class BaseMessage(DataNode):
    """
    Represents a message in a chatbot-like system, inheriting from BaseNode.

    Attributes:
            role (str | None): The role of the entity sending the message, e.g., 'user', 'system'.
            sender (str | None): The identifier of the sender of the message.
            content (Any): The actual content of the message.
    """

    role: str | None = None
    sender: str | None = None
    recipient: str | None = None

    @property
    def msg(self) -> dict:
        """
        Constructs and returns a dictionary representation of the message.

        Returns:
                A dictionary representation of the message with 'role' and 'content' keys.
        """
        return self._to_message()

    @property
    def msg_content(self) -> str | dict:
        """
        Gets the 'content' field of the message.

        Returns:
                The 'content' part of the message.
        """
        return self.msg["content"]

    def _to_message(self):
        """
        Constructs and returns a dictionary representation of the message.

        Returns:
                dict: A dictionary representation of the message with 'role' and 'content' keys.
        """
        return {"role": self.role, "content": convert.to_str(self.content)}

    def __str__(self):
        content_preview = (
            f"{str(self.content)[:75]}..."
            if self.content and len(self.content) > 75
            else str(self.content)
        )
        return f"Message(role={self.role}, sender={self.sender}, content='{content_preview}')"


class Instruction(BaseMessage):
    """
    Represents an instruction message, a specialized subclass of Message.

    This class is specifically used for creating messages that are instructions from the user,
    including any associated context. It sets the message role to 'user'.
    """

    def __init__(
        self,
        instruction: dict | list | str,
        context=None,
        sender: str | None = None,
        output_fields=None,
        recipient=None,
    ):  # sourcery skip: avoid-builtin-shadow
        super().__init__(
            role="user",
            sender=sender or "user",
            content={"instruction": instruction},
            recipient=recipient or "assistant",
        )
        if context:
            self.content.update({"context": context})

        if output_fields:
            format = f"""
            Follow the following response format.
            ```json
            {output_fields}
            ```         
            """
            self.content.update({"response_format": format})

    @property
    def instruct(self):
        return self.content["instruction"]


class System(BaseMessage):
    """
    Represents a system-related message, a specialized subclass of Message.

    Designed for messages containing system information, this class sets the message role to 'system'.
    """

    def __init__(
        self, system: dict | list | str, sender: str | None = None, recipient=None
    ):
        super().__init__(
            role="system",
            sender=sender or "system",
            content={"system_info": system},
            recipient=recipient or "assistant",
        )

    @property
    def system_info(self):
        return self.content["system_info"]


class Response(BaseMessage):
    """
    Represents a response message, a specialized subclass of Message.

    Used for various types of response messages including regular responses, action requests,
    and action responses. It sets the message role to 'assistant'.

    """

    def __init__(
        self, response: dict | list | str, sender: str | None = None, recipient=None
    ) -> None:
        content_key = ""
        try:
            response = response["message"]
            if convert.strip_lower(response["content"]) == "none":
                content_ = self._handle_action_request(response)
                sender = sender or "action_request"
                content_key = content_key or "action_request"
                recipient = recipient or "action"

            else:
                try:
                    if "tool_uses" in convert.to_dict(response["content"]):
                        content_ = convert.to_dict(response["content"])["tool_uses"]
                        content_key = content_key or "action_request"
                        sender = sender or "action_request"
                        recipient = recipient or "action"

                    elif "response" in convert.to_dict(response["content"]):
                        sender = sender or "assistant"
                        content_key = content_key or "response"
                        content_ = convert.to_dict(response["content"])["response"]
                        recipient = recipient or "user"

                    elif "action_request" in convert.to_dict(response["content"]):
                        sender = sender or "action_request"
                        content_key = content_key or "action_request"
                        content_ = convert.to_dict(response["content"])[
                            "action_request"
                        ]
                        recipient = recipient or "action"

                    else:
                        content_ = response["content"]
                        content_key = content_key or "response"
                        sender = sender or "assistant"
                        recipient = recipient or "user"
                except Exception:
                    content_ = response["content"]
                    content_key = content_key or "response"
                    sender = sender or "assistant"
                    recipient = recipient or "user"

        except Exception:
            sender = sender or "action_response"
            content_ = response
            content_key = content_key or "action_response"
            recipient = recipient or "assistant"

        super().__init__(
            role="assistant",
            sender=sender,
            content={content_key: content_},
            recipient=recipient,
        )

    @staticmethod
    def _handle_action_request(response):
        """
        Processes an action request response and extracts relevant information.

        Args:
                response (dict): The response dictionary containing tool calls and other information.

        Returns:
                list: A list of dictionaries, each representing a function call with action and arguments.

        Raises:
                ValueError: If the response does not conform to the expected format for action requests.
        """
        try:
            tool_count = 0
            func_list = []
            while tool_count < len(response["tool_calls"]):
                _path = ["tool_calls", tool_count, "type"]

                if nested.nget(response, _path) == "function":
                    _path1 = ["tool_calls", tool_count, "function", "name"]
                    _path2 = ["tool_calls", tool_count, "function", "arguments"]

                    func_content = {
                        "action": f"action_{nested.nget(response, _path1)}",
                        "arguments": nested.nget(response, _path2),
                    }
                    func_list.append(func_content)
                tool_count += 1
            return func_list
        except:
            raise ValueError(
                "Response message must be one of regular response or function calling"
            )


# class BaseMessage(DataNode):


#     def __init__():
#         ...

#     role: MessageRoleType = Field(..., alias=MessageField.ROLE.value)
#     sender: str = Field(..., alias=MessageField.SENDER.value)  # Customizable sender
#     recipient: str | None = Field(None,
#                                      alias=MessageField.RECIPIENT.value)  # Optional recipient

#     class Config:
#         extra = 'allow'
#         use_enum_values = True
#         populate_by_name = True

#     @model_validator(mode='before')
#     def handle_extra_fields(cls, values):
#         """Move undefined fields to metadata."""
#         fields = set(values.keys())
#         defined_fields = set(cls.model_fields.keys())
#         extra_fields = fields - defined_fields

#         if extra_fields:
#             metadata = values.get('metadata', {})
#             for field in extra_fields:
#                 if field in metadata:
#                     metadata[f"{field}_1"] = values.pop(field)
#                 else:
#                     metadata[field] = values.pop(field)
#             values['metadata'] = metadata
#         return values

#     def _to_roled_message(self):
#         return {
#             MessageField.ROLE.value: self.role.value,
#             MessageField.CONTENT.value: (
#                 json.dumps(self.content) if isinstance(self.content, dict)
#                 else self.content
#             )
#         }

#     def to_pd_series(self, *args, **kwargs):
#         msg_dict = self.to_dict(*args, **kwargs)
#         if isinstance(to_dict(msg_dict['content']), dict):
#             msg_dict['content'] = json.dumps(msg_dict['content'])
#         return pd.Series(msg_dict)

#     @classmethod
#     def from_pd_series(cls, series: pd.Series, **kwargs):
#         self = cls.from_dict(series.to_dict(**kwargs))
#         if isinstance(self.content, str):
#             try:
#                 self.content = to_dict(self.content)
#             except:
#                 pass
#         return self


#     def __str__(self):
#         content_preview = self.content[:50] + "..." if len(
#             self.content) > 50 else self.content
#         meta_preview = str(self.metadata)[:50] + "..." if len(
#             str(self.metadata)) > 50 else str(self.metadata)

#         return (
#             f"Message({self.role.value or 'none'}, {self._sender or 'none'}, "
#             f"{content_preview or 'none'}, {self.recipient or 'none'},"
#             f"{self.timestamp or 'none'}, {meta_preview or 'none'}"
#         )

# class Instruction(BaseMessage):

#     def __init__(self, instruction: Any, context: Any = None,
#                  sender: str | None = None, recipient: str | None | Any = None,
#                  metadata: dict | None = None, relation: list | None | Any = None,
#                  **kwargs):
#         super().__init__(
#             role=MessageType.INSTRUCTION.value[MessageField.ROLE.value],
#             sender=sender or MessageType.INSTRUCTION.value[MessageField.SENDER.value],
#             content={MessageType.INSTRUCTION.value["content_key"]: instruction},
#             recipient=recipient or MessageType.SYSTEM.value[MessageField.RECIPIENT.value],
#             metadata=metadata or {}, relation=relation or [], **kwargs
#         )
#         if context:
#             self.content.update({MessageType.CONTEXT.value["content_key"]: context})


# class System(BaseMessage):

#     def __init__(self, system: Any, sender: str | None = None, recipient: Optional[
#         str] = None, metadata: Optional[dict] = None, relation: Optional[list] = None,
#                  **kwargs):
#         super().__init__(
#             role=MessageType.SYSTEM.value[MessageField.ROLE.value],
#             sender=sender or MessageType.SYSTEM.value[MessageField.SENDER.value],
#             content={MessageType.SYSTEM.value["content_key"]: system},
#             recipient=recipient or MessageType.SYSTEM.value[MessageField.RECIPIENT.value],
#             metadata=metadata or {}, relation=relation or [], **kwargs
#         )


# class ActionRequest(BaseMessage):

#     def __init__(self, action_request: Any, sender: str | None = None,
#                  recipient: Optional[
#                      str] = None, metadata: Optional[dict] = None,
#                  relation: Optional[list] = None,
#                  **kwargs
#                  ):

#         super().__init__(
#             role=MessageType.ACTION_REQUEST.value[MessageField.ROLE.value],
#             sender=sender or MessageType.ACTION_REQUEST.value[MessageField.SENDER.value],
#             content={MessageType.ACTION_REQUEST.value["content_key"]: action_request},
#             recipient=recipient or MessageType.ACTION_REQUEST.value[
#                 MessageField.RECIPIENT.value],
#             metadata=metadata or {}, relation=relation or [], **kwargs
#         )

#     @classmethod
#     def from_response(cls, response, sender=None, recipient=None, metadata=None,
#                       relation=None,
#                       **kwargs):
#         return cls(action_request=response, sender=sender, recipient=recipient,
#                    metadata=metadata,
#                    relation=relation, **kwargs)

#     @staticmethod
#     def _handle_action_request(response):
#         try:
#             tool_count = 0
#             func_list = []
#             while tool_count < len(response['tool_calls']):
#                 _path = ['tool_calls', tool_count, 'type']

#                 if nget(response, _path) == 'function':
#                     _path1 = ['tool_calls', tool_count, 'function', 'name']
#                     _path2 = ['tool_calls', tool_count, 'function', 'arguments']

#                     func_content = {
#                         "action": ("action_" + nget(response, _path1)),
#                         "arguments": nget(response, _path2)
#                     }
#                     func_list.append(func_content)
#                 tool_count += 1
#             return func_list
#         except:
#             raise ValueError(
#                 "Response message must be one of regular response or function calling"
#             )


# class ActionResponse(BaseMessage):

#     def __init__(self, action_response: Any, sender: str | None = None,
#                  recipient: Optional[
#                      str] = None, metadata: Optional[dict] = None,
#                  relation: Optional[list] = None,
#                  **kwargs
#                  ):
#         super().__init__(
#             role=MessageType.ACTION_RESPONSE.value[MessageField.ROLE.value],
#             sender=sender or MessageType.ACTION_RESPONSE.value[MessageField.SENDER.value],
#             content={MessageType.ACTION_RESPONSE.value["content_key"]: action_response},
#             recipient=recipient or MessageType.ACTION_RESPONSE.value[
#                 MessageField.RECIPIENT.value],
#             metadata=metadata or {}, relation=relation or [], **kwargs
#         )

#     @classmethod
#     def from_response(cls, response, sender=None, recipient=None, metadata=None,
#                       relation=None,
#                       **kwargs):
#         return cls(action_response=response, sender=sender, recipient=recipient,
#                    metadata=metadata,
#                    relation=relation, **kwargs)


# class AssistantResponse(BaseMessage):

#     def __init__(self, response: Any, sender: str | None = None,
#                  recipient: Optional[
#                      str] = None, metadata: Optional[dict] = None,
#                  relation: Optional[list] = None,
#                  **kwargs
#                  ):
#         super().__init__(
#             role='assistant',
#             sender=sender or MessageType.RESPONSE.value[MessageField.SENDER.value],
#             content={MessageType.RESPONSE.value["content_key"]: response},
#             recipient=recipient or MessageType.RESPONSE.value[
#                 MessageField.RECIPIENT.value],
#             metadata=metadata or {}, relation=relation or [], **kwargs
#         )

#     @classmethod
#     def from_response(cls, response, sender=None, recipient=None, metadata=None,
#                       relation=None,
#                       **kwargs):
#         return cls(response=response, sender=sender, recipient=recipient,
#                    metadata=metadata,
#                    relation=relation, **kwargs)
