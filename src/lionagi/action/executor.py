# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Iterator
from typing import Any

from typing_extensions import override

from ..protocols.types import ID, BaseExecutor, EventStatus, Pile, Progression
from .base import Action
from .processor import ActionProcessor

__all__ = ("ActionExecutor",)


class ActionExecutor(BaseExecutor):
    """Executes and manages asynchronous actions with status tracking.

    Handles action queuing, processing, and status management using a configured
    processor. Supports both strict and non-strict type checking modes.
    """

    processor_class: type[ActionProcessor] = ActionProcessor
    strict: bool = True

    @override
    def __init__(self, **kwargs: Any) -> None:
        """Initialize executor with processor configuration.

        Args:
            **kwargs: Configuration options passed to the processor.
        """
        super().__init__(**kwargs)
        self.pile: Pile[Action] = Pile(
            item_type={self.processor_class.event_type},
            strict_type=False,  # Allow subclasses of Action
        )
        self.pending: Progression = Progression()
        self.processor: ActionProcessor = None

    @property
    def pending_action(self) -> Pile[Action]:
        """Get pile of actions with pending status."""
        return Pile(
            items=[i for i in self.pile if i.status == EventStatus.PENDING],
        )

    @property
    def completed_action(self) -> Pile[Action]:
        """Get pile of actions with completed status."""
        return Pile(
            items=[i for i in self.pile if i.status == EventStatus.COMPLETED],
        )

    async def append(self, action: Action) -> None:
        """Add new action to executor and pending queue.

        Args:
            action: Action instance to append.
        """
        async with self.pile:
            self.pile.include(action)  # Pass as positional argument
            self.pending.include(action)  # Pass as positional argument

    @override
    async def forward(self) -> None:
        """Process all pending actions through configured processor."""
        while len(self.pending) > 0:
            action = self.pile[self.pending.popleft()]
            await self.processor.enqueue(action)
        await self.processor.process()

    def __contains__(self, action: ID[Action].Ref) -> bool:
        """Checks if an action is present in the pile."""
        return action in self.pile

    def __iter__(self) -> Iterator[Action]:
        """Iterate over all actions in pile."""
        return iter(self.pile)
