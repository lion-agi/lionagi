"""Test action implementation for unit tests."""

import asyncio
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from lionagi.action.base import Action
from lionagi.protocols.types import EventStatus, IDType


class TestAction(Action):
    """Concrete Action implementation for testing."""

    def __init__(
        self,
        test_result: Any | None = None,
        test_error: str | None = None,
        test_delay: float = 0.1,
        **kwargs: Any,
    ) -> None:
        """Initialize test action with configurable behavior.

        Args:
            test_result: Result to return on successful execution
            test_error: Error to raise during execution
            test_delay: Time to sleep during execution
            **kwargs: Additional arguments for Action initialization
        """
        # Set default values for BaseAutoModel fields
        kwargs.setdefault("id", IDType(uuid4().hex))
        kwargs.setdefault("created_timestamp", datetime.now().timestamp())
        kwargs.setdefault("status", EventStatus.PENDING)
        kwargs.setdefault("execution_time", None)
        kwargs.setdefault("execution_result", None)
        kwargs.setdefault("error", None)

        super().__init__(**kwargs)
        self._test_result = test_result or {"test": "result"}
        self._test_error = test_error
        self._test_delay = test_delay

    async def invoke(self) -> None:
        """Test implementation of abstract invoke method."""
        start = asyncio.get_event_loop().time()
        self.status = EventStatus.PROCESSING

        try:
            # Use real sleep to test timing
            await asyncio.sleep(self._test_delay)

            if self._test_error:
                raise ValueError(self._test_error)

            self.execution_time = asyncio.get_event_loop().time() - start
            self.execution_result = self._test_result
            self.status = EventStatus.COMPLETED

        except Exception as e:
            self.execution_time = asyncio.get_event_loop().time() - start
            self.error = str(e)
            self.status = EventStatus.FAILED
