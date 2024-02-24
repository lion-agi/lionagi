from pydantic import BaseModel, Field, model_validator, ValidationError
from lionagi.schema.base_node import BaseNode
from lionagi.util.sys_util import SysUtil
from ..schema import MessageField, MessageRoleType



class BaseMessage(BaseNode):
    role: MessageRoleType = Field(..., alias=MessageField.ROLE.value)
    sender: str = Field(..., alias=MessageField.SENDER.value)  # Customizable sender
    recipient: Optional[str] = Field(None, alias=MessageField.RECIPIENT.value)  # Optional recipient


    class Config:
        extra = 'allow'
        use_enum_values = True
        allow_population_by_field_name = True

    @model_validator(pre=True)
    def handle_extra_fields(cls, values):
        """Move undefined fields to metadata."""
        fields = set(values.keys())
        defined_fields = set(cls.__fields__.keys())
        extra_fields = fields - defined_fields

        if extra_fields:
            metadata = values.get('metadata', {})
            for field in extra_fields:
                metadata[field] = values.pop(field)
            values['metadata'] = metadata
        return values


























    @property
    def content_str(self):
        if isinstance(self.content, Dict):
            return json.dumps(self.content)
        elif isinstance(self.content, str):
            return self.content
        else:
            try:
                return str(self.content)
            except ValueError:
                print(f"Content is not serializable for Node: {self._id}")
                return 'null'

    @property
    def dict(self, **kwargs):
        return {
            'node_id': self.id_,
            'metadata': self.metadata or 'null',
            'timestamp': self.timestamp,
            'role': self.role,
            'sender': self._sender,
            'recipient': self.recipient,
            'content': self.content_str,
        }

    @property
    def to_pd_series(self):
        return pd.Series(self.dict)

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, sender):
        self._sender = sender

    @property
    def msg_sender(self) -> str:
        return self.roled_msg[MessageField.SENDER.value]

    @property
    def msg_recipient(self) -> str:
        return self.roled_msg[MessageField.RECIPIENT.value]

    @property
    def msg_timestamp(self) -> Any:
        return self.roled_msg[MessageField.TIMESTAMP.value]

    @property
    def as_pd_series(self) -> pd.Series:
        return pd.Series(self.roled_msg)

    def add_recipient(self, recipient: str) -> None:
        self.recipient = recipient

    def _to_roled_message(self):
        return {
            MessageField.ROLE.value: self._role.value,
            MessageField.CONTENT.value: (
                json.dumps(self.content) if isinstance(self.content, dict)
                else self.content
            )
        }

    def __str__(self):
        content_preview = (
            (str(self.content)[:75] + '...') if self.content and len(self.content) > 75
            else str(self.content)
        )
        return (
            f"Message({MessageField.ROLE.value}={self._role.value or 'none'}, \
                {MessageField.SENDER.value}={self._sender or 'none'}, \
                {MessageField.CONTENT.value}='{content_preview or 'none'}, \
                {MessageField.RECIPIENT.value}={self.recipient or 'none'}, \
                {MessageField.TIMESTAMP.value}={self.timestamp or 'none'})"
        )
