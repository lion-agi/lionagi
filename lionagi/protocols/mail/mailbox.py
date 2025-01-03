# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.protocols.generic.element import IDType

from ..generic.pile import Pile, Progression
from .mail import Mail

__all__ = ("Mailbox",)


class Mailbox:

    def __init__(self):
        self.pile_ = Pile(item_type=Mail, strict_type=True)
        self.pending_ins: dict[IDType, Progression] = {}
        self.pending_outs = Progression()

    def __contains__(self, item: Mail) -> bool:
        return item in self.pile_

    @property
    def senders(self) -> list[str]:
        return list(self.pending_ins.keys())

    def append_in(self, item: Mail, /):
        if item.sender not in self.pending_ins:
            self.pending_ins[item.sender] = Progression()
        self.pending_ins[item.sender].include(item)
        self.pile_.include(item)

    def append_out(self, item: Mail, /):
        self.pending_outs.include(item)
        self.pile_.include(item)

    def exclude(self, item: Mail, /):
        self.pile_.exclude(item)
        self.pending_outs.exclude(item)
        for v in self.pending_ins.values():
            v.exclude(item)

    def __bool__(self) -> bool:
        return bool(self.pile_)

    def __len__(self) -> int:
        return len(self.pile_)
