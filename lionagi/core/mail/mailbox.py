from ..generic.abc import Element, Field
from ..generic import Pile, Progression, pile, progression
from .mail import Mail


class MailBox(Element):
    pile: Pile[Mail] = Field(
        default_factory=lambda: pile({}, Mail),
        description="The pile of all mails - {mail_id: Mail}",
    )
    
    sequence_in: Pile[Progression] = Field(
        default_factory=lambda: pile({}, Progression),
        description="The sequences of all mails - {sequence_id: Progression}",
    )

    sequence_out: Progression = Field(
        default_factory=progression,
        description="The sequence of all outgoing mails - deque[mail_id]",
    )

    def __str__(self) -> str:
        """
        Returns a string representation of the MailBox instance.

        Returns:
            str: A string describing the number of pending incoming and
                outgoing mails in the MailBox.
        """
        return (
            f"Mailbox with {len(self.pile)} pending items"
            f", {self.sequence_in.size()} pending incoming mails and "
            f"{len(self.sequence_out)} pending outgoing mails."
        )
