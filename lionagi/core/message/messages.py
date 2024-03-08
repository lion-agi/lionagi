from typing import Any
from lionagi.integrations.bridge.pydantic_ import base_model as pyd
from lionagi.libs import ln_nested as nested
from lionagi.libs import ln_convert as convert
from lionagi.libs import ln_dataframe as dataframe

from lionagi.core.message.schema import (
    MessageField,
    MessageRoleType,
    MessageType,
)

from lionagi.core.schema.structure import Relationship
from lionagi.core.schema.data_node import DataNode



class BaseMessage(DataNode):
    role: MessageRoleType = pyd.Field(..., alias=MessageField.ROLE.value)
    sender: str = pyd.Field(..., alias=MessageField.SENDER.value)
    recipient: str = pyd.Field(..., alias=MessageField.RECIPIENT.value)
    relationship: list[Relationship] = pyd.Field([],
                                                 alias=MessageField.RELATIONSHIP.value)

    class Config:
        extra = 'allow'
        use_enum_values = True
        populate_by_name = True

    @pyd.model_validator(mode='before')
    def handle_extra_fields(cls, values):
        """Move undefined fields to metadata."""
        fields = set(values.keys())
        defined_fields = set(cls.model_fields.keys())
        extra_fields = fields - defined_fields

        if extra_fields:
            metadata = values.get('metadata', {})
            for field in extra_fields:
                if field in metadata:
                    metadata[f"{field}_1"] = values.pop(field)
                else:
                    metadata[field] = values.pop(field)
            values['metadata'] = metadata
        return values

    @property
    def msg(self) -> dict:
        return self._to_roled_message()

    @property
    def msg_content(self) -> str | dict:
        return self.msg["content"]

    def _to_roled_message(self):
        out = {
            MessageField.ROLE.value: self.role,
            MessageField.CONTENT.value: convert.to_str(self.content)
        }
        return out

    def __str__(self):
        content_preview = (
            (str(self.content)[:75] + "...")
            if self.content and len(self.content) > 75
            else str(self.content)
        )
        return f"Message(role={self.role}, sender={self.sender}, content='{content_preview}')"

    def to_pd_series(self, *args, **kwargs):

        msg_dict = self.to_dict(*args, **kwargs)
        out = {
            MessageField.ROLE.value: msg_dict.pop(MessageField.ROLE.value),
            MessageField.SENDER.value: msg_dict.pop(MessageField.SENDER.value),
            MessageField.RECIPIENT.value: msg_dict.pop(MessageField.RECIPIENT.value),
            MessageField.TIMESTAMP.value: msg_dict.pop(MessageField.TIMESTAMP.value),
            MessageField.CONTENT.value: msg_dict.pop(MessageField.CONTENT.value),
            MessageField.RELATIONSHIP.value: convert.to_str(
                msg_dict.pop(MessageField.RELATIONSHIP.value)
            ),
        }

        if msg_dict != {}:
            self.metadata_merge(msg_dict)

        out[MessageField.METADATA.value] = convert.to_str(self.metadata)

        return dataframe.ln_Series(out)


class Instruction(BaseMessage):

    def __init__(self, instruction: Any, context: Any = None, sender: str = None,
                 recipient: str = None, relation: list[Relationship] = None, **kwargs):

        super().__init__(**kwargs)
        self.role = MessageType.INSTRUCTION.value[MessageField.ROLE.value]
        self.sender = sender or MessageType.INSTRUCTION.value[MessageField.SENDER.value]
        self.recipient = recipient or MessageType.INSTRUCTION.value[MessageField.RECIPIENT.value]
        self.relationship = relation or []

        self.content = {MessageType.INSTRUCTION.value["content_key"]: instruction}
        if context:
            self.content.update({MessageType.CONTEXT.value["content_key"]: context})


class System(BaseMessage):

    def __init__(self, system: Any, sender: str = None, recipient: str = None,
                 relation: list[Relationship] = None, **kwargs):

        super().__init__(**kwargs)
        self.role = MessageType.SYSTEM.value[MessageField.ROLE.value]
        self.sender = sender or MessageType.SYSTEM.value[MessageField.SENDER.value]
        self.recipient = recipient or MessageType.SYSTEM.value[MessageField.RECIPIENT.value]
        self.relationship = relation or []

        system = system or "you are a helpful assistant"
        self.content = {MessageType.SYSTEM.value["content_key"]: system}


class ActionRequest(BaseMessage):
    def __init__(self, action_request: Any, sender: str = None,
                 recipient: str = None, relation: list[Relationship] = None, **kwargs):

        super().__init__(**kwargs)
        self.role = MessageType.ACTION_REQUEST.value[MessageField.ROLE.value]
        self.sender = sender or MessageType.ACTION_REQUEST.value[MessageField.SENDER.value]
        self.recipient = recipient or MessageType.ACTION_REQUEST.value[MessageField.RECIPIENT.value]
        self.relationship = relation or []
        self.content = {MessageType.ACTION_REQUEST.value["content_key"]: action_request}

    @classmethod
    def from_response(cls, response, **kwargs):
        return cls(action_request=response, **kwargs)

    @staticmethod
    def handle_action_request(response):
        try:
            tool_count = 0
            func_list = []
            while tool_count < len(response["tool_calls"]):
                _path = ["tool_calls", tool_count, "type"]

                if nested.nget(response, _path) == "function":
                    _path1 = ["tool_calls", tool_count, "function", "name"]
                    _path2 = ["tool_calls", tool_count, "function", "arguments"]

                    func_content = {
                        "action": ("action_" + nested.nget(response, _path1)),
                        "arguments": nested.nget(response, _path2),
                    }
                    func_list.append(func_content)
                tool_count += 1
            return func_list
        except:
            raise ValueError(
                "Response message must be one of regular response or function calling"
            )


class ActionResponse(BaseMessage):

    def __init__(self, action_response: Any, sender: str = None,
                 recipient: str = None, relation: list[Relationship] = None, **kwargs):
        super().__init__(**kwargs)
        self.role = MessageType.ACTION_RESPONSE.value[MessageField.ROLE.value]
        self.sender = sender or MessageType.ACTION_RESPONSE.value[
            MessageField.SENDER.value]
        self.recipient = recipient or MessageType.ACTION_RESPONSE.value[
            MessageField.RECIPIENT.value]
        self.relationship = relation or []
        self.content = {MessageType.ACTION_RESPONSE.value["content_key"]: action_response}

    @classmethod
    def from_response(cls, response, **kwargs):
        return cls(action_response=response, **kwargs)



class AssistantResponse(BaseMessage):

    def __init__(self, response: Any, sender: str = None,
                 recipient: str = None, relation: list[Relationship] = None, **kwargs):
        super().__init__(**kwargs)
        self.role = MessageType.RESPONSE.value[MessageField.ROLE.value]
        self.sender = sender or MessageType.RESPONSE.value[MessageField.SENDER.value]
        self.recipient = recipient or MessageType.RESPONSE.value[MessageField.RECIPIENT.value]
        self.relationship = relation or []
        self.content = {MessageType.RESPONSE.value["content_key"]: response}

    @classmethod
    def from_response(cls, response, **kwargs):
        return cls(response=response, **kwargs)


class Response:

    @staticmethod
    def process(response: dict | list | str, **kwargs) -> BaseMessage:
        try:
            response = response["message"]

            if convert.strip_lower(response["content"]) == "none":
                content_ = ActionRequest.handle_action_request(response)
                return ActionRequest.from_response(content_, **kwargs)

            else:
                try:

                    if "tool_uses" in convert.to_dict(response["content"]):
                        content_ = convert.to_dict(response["content"])["tool_uses"]
                        return ActionRequest.from_response(content_, **kwargs)

                    elif "response" in convert.to_dict(response["content"]):
                        content_ = convert.to_dict(response["content"])["response"]
                        return AssistantResponse.from_response(content_, **kwargs)

                    elif "action_request" in convert.to_dict(response["content"]):
                        content_ = convert.to_dict(response["content"])["action_request"]
                        return ActionRequest.from_response(content_, **kwargs)

                    else:
                        content_ = response["content"]
                        return AssistantResponse.from_response(content_, **kwargs)

                except:
                    content_ = response["content"]
                    return AssistantResponse.from_response(content_, **kwargs)

        except:
            content_ = response
            return ActionResponse.from_response(content_, **kwargs)
