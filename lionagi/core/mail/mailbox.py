from ..generic.abc import Element, Field
from ..generic import Pile, Progression, pile, progression
from .mail import Mail


class MailBox(Element):
    pile: Pile[Mail] = Field(
        default_factory=lambda: pile({}, Mail),
        description="The pile of all mails - {mail_id: Mail}",
    )

    pending_ins: dict[str, Progression] = Field(
        default_factory=dict,
        description="The sequences of all mails - {sender_id: Progression}",
    )

    pending_outs: Progression = Field(
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
            f", {self.pending_ins.size()} pending incoming mails and "
            f"{len(self.pending_outs)} pending outgoing mails."
        )

    def include(self, mail, direction="in"):
        if direction == "in":
            if mail.sender not in self.pending_ins:
                self.pending_ins[mail.sender] = progression()
            return self.pile.include(mail) and self.pending_ins[mail.sender].include(
                mail
            )

        return self.pile.include(mail) and self.pending_outs.include(mail)
