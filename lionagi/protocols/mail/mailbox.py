# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Implements a simple mailbox system for each Communicatable entity.
Holds inbound and outbound mail, stored internally in a `Pile`.
"""

import asyncio
from typing import Any

from lionagi._errors import TimeoutError
from lionagi.protocols.generic.element import IDType

from ..generic.pile import Pile, Progression
from .mail import Mail

__all__ = ("Mailbox",)


class Mailbox:
    """
    A mailbox that accumulates inbound and outbound mail for a single
    communicatable source.

    Attributes
    ----------
    pile_ : Pile[Mail]
        A concurrency-safe collection storing all mail items.
    pending_ins : dict[IDType, Progression]
        Maps each sender's ID to a progression of inbound mail.
    pending_outs : Progression
        A progression of mail items waiting to be sent (outbound).
    """

    def __init__(self):
        """
        Initialize an empty Mailbox with separate tracks for inbound
        and outbound mail.
        """
        self.pile_ = Pile(item_type=Mail, strict_type=True)
        self.pending_ins: dict[IDType, Progression] = {}
        self.pending_outs = Progression()
        self._response_events: dict[str, asyncio.Event] = {}
        self._responses: dict[str, Any] = {}

    def __contains__(self, item: Mail) -> bool:
        """
        Check if a mail item is currently in this mailbox.
        """
        return item in self.pile_

    @property
    def senders(self) -> list[str]:
        """
        List of sender IDs that have inbound mail in this mailbox.

        Returns
        -------
        list[str]
        """
        return list(self.pending_ins.keys())

    def append_in(self, item: Mail, /):
        """
        Add a mail item to the inbound queue for the item's sender.
        If this is a response to a pending ask, trigger the event.

        Parameters
        ----------
        item : Mail
        """
        if item.sender not in self.pending_ins:
            self.pending_ins[item.sender] = Progression()
        self.pending_ins[item.sender].include(item)
        self.pile_.include(item)

        # Check if this is a response to a pending ask
        if (
            item.package.request_source
            and item.package.request_source in self._response_events
        ):
            self._responses[item.package.request_source] = item.package.item
            event = self._response_events[item.package.request_source]
            event.set()

    def append_out(self, item: Mail, /):
        """
        Add a mail item to the outbound (pending_outs) queue.

        Parameters
        ----------
        item : Mail
        """
        self.pending_outs.include(item)
        self.pile_.include(item)

    def exclude(self, item: Mail, /):
        """
        Remove a mail item from all internal references (inbound, outbound, and pile).

        Parameters
        ----------
        item : Mail
        """
        self.pile_.exclude(item)
        self.pending_outs.exclude(item)
        for v in self.pending_ins.values():
            v.exclude(item)

    async def await_response(self, ask_id: str, timeout: int = 30) -> Any:
        """
        Wait for a response to a specific ask request.

        Parameters
        ----------
        ask_id : str
            The ID of the ask request to wait for
        timeout : int
            Maximum time to wait in seconds

        Returns
        -------
        Any
            The response content

        Raises
        ------
        TimeoutError
            If no response is received within the timeout period
        """
        # Create event for this ask_id if it doesn't exist
        if ask_id not in self._response_events:
            self._response_events[ask_id] = asyncio.Event()

        try:
            # Wait for response with timeout
            await asyncio.wait_for(
                self._response_events[ask_id].wait(), timeout
            )

            # Get and clean up response
            response = self._responses.pop(ask_id)
            self._response_events.pop(ask_id)
            return response

        except asyncio.TimeoutError:
            # Clean up on timeout
            self._response_events.pop(ask_id, None)
            self._responses.pop(ask_id, None)
            raise TimeoutError(
                f"No response received for ask_id {ask_id} within {timeout} seconds"
            )

    def __bool__(self) -> bool:
        """
        Indicates if the mailbox contains any mail.
        """
        return bool(self.pile_)

    def __len__(self) -> int:
        """
        Number of mail items in this mailbox.
        """
        return len(self.pile_)
