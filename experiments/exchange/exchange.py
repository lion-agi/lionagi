from typing import Any
from functools import singledispatchmethod
from collections import deque
from pydantic import Field, field_validator
from lionagi.core.generic import Node
from lionagi.core.generic.mail import Mail, MailBox, MailPackageCategory, PostBox


class Exchange(Node):
    postbox: PostBox = Field(
        default_factory=PostBox,
        description="The postbox for outgoing mails."
    )
    
    sources: dict[str, Node] = Field(
        default_factory=dict,
        description="The sources of the exchange."
    )
    
    @field_validator("sources", mode="before")
    def _validate_source(cls, value):
        if isinstance(value, (list, Node)):
            return {
                v.id_: v for v in (value if isinstance(value, list) else [value])
            }
        return value
    
    @singledispatchmethod
    def add_source(self, sources: Any):
        raise ValueError("Failed to add source, please input Node, list or dict")

    @add_source.register
    def _(self, sources: Node):
        if sources.id_ not in self.sources:
            self.sources[sources.id_] = sources
            
            
            self.mailbox.sending[sources.id_] = {}

    @add_source.register
    def _(self, sources: list):
        for v in sources:
            self.add_source(v)

    
    
    """
    def collect: collect mails from a mailbox to a postbox
    def deliver: deliver mails from a postbox to mail boxes
    """
    
    
    
    