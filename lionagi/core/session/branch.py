from lion_core.session.branch import Branch as CoreBranch

from typing import Any
from lionagi.libs.ln_convert import to_df
from lionagi.core.collections.abc import Field
from lionagi.core.generic.pile import Pile, pile


from lionagi.core.generic.node import Node


class Branch(CoreBranch, Node):

    messages: Pile | None = Field(default_factory=pile)

    def clear(self) -> None:
        """
        Clears all messages and progression in the branch.
        """
        self.messages.clear()
        self.progress.clear()

    def to_df(self) -> Any:
        """
        Converts the messages to a DataFrame.

        Returns:
            Any: A DataFrame representation of the messages.
        """
        fields = [
            "ln_id",
            "message_type",
            "timestamp",
            "role",
            "content",
            "metadata",
            "sender",
            "recipient",
        ]
        dicts_ = []
        for i in self.progress:
            _d = {}
            for j in fields:
                _d.update({j: getattr(self.messages[i], j, None)})
                _d["message_type"] = self.messages[i].class_name()
            dicts_.append(_d)

        return to_df(dicts_)
