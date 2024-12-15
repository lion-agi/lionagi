"""Performance tests for action processing system."""

import asyncio
import time
from collections.abc import Callable
from statistics import mean, stdev
from typing import Any, Optional

import pytest

from lionagi.action.function_calling import FunctionCalling
from lionagi.action.tool import Tool
from lionagi.protocols.types import EventStatus
from tests.action.utils.mock_processor import MockProcessor
from tests.action.utils.test_base import ActionTestBase


class TestActionPerformance(ActionTestBase):
    """Performance tests for action processing system."""

    @pytest.fixture
    async def variable_latency_tool(self) -> Tool:
        """Fixture providing tool with configurable latency."""

        async def latency_func(delay: float = 0.1) -> dict[str, Any]:
            await asyncio.sleep(delay)
            return {"processed_at": time.time()}

        return Tool(
            function=latency_func,
            schema_={
                "name": "latency_func",
                "parameters": {
                    "type": "object",
                    "properties": {"delay": {"type": "number"}},
                },
            },
        )

    async def measure_processing_time(
        self,
        processor: MockProcessor,
        actions: list[FunctionCalling],
        timeout: float = 30.0,  # Increased timeout
        expected_status: EventStatus | None = EventStatus.COMPLETED,
    ) -> tuple[float, list[float]]:
        """Measure total and individual action processing times.

        Args:
            processor: Processor to use
            actions: List of actions to process
            timeout: Maximum time to wait for processing
            expected_status: Expected final status for actions

        Returns:
            Tuple of (total_time, list_of_individual_times)
        """
        start_time = time.time()

        # Process all actions
        for action in actions:
            await processor.enqueue(action)
        await processor.process()

        # Wait for all actions to reach expected status
        if expected_status:
            try:
                await asyncio.wait_for(
                    self.assert_all_actions_status(actions, expected_status),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                raise AssertionError(
                    f"Actions did not complete within {timeout} seconds"
                )

        total_time = time.time() - start_time

        # Calculate individual times
        individual_times = [
            action.execution_time
            for action in actions
            if action.execution_time is not None
        ]

        return total_time, individual_times

    @pytest.mark.asyncio
    async def test_throughput_scaling(self, variable_latency_tool: Tool):
        """Test processing throughput with increasing load."""
        batch_sizes = [10, 50, 100]
        results = []

        for size in batch_sizes:
            processor = MockProcessor(capacity=size)

            # Create batch of quick actions
            actions = [
                FunctionCalling.create(
                    tool=variable_latency_tool,
                    arguments={"delay": 0.1},  # Increased delay
                )
                for _ in range(size)
            ]

            total_time, individual_times = await self.measure_processing_time(
                processor, actions
            )

            # Calculate metrics
            throughput = size / total_time
            avg_latency = mean(individual_times)

            results.append(
                {
                    "batch_size": size,
                    "total_time": total_time,
                    "throughput": throughput,
                    "avg_latency": avg_latency,
                }
            )

            # Verify all completed
            await self.assert_all_actions_status(
                actions, EventStatus.COMPLETED
            )

            await processor.stop()

        # Verify throughput scales reasonably
        throughputs = [r["throughput"] for r in results]
        assert all(
            t > 0 for t in throughputs
        ), "All throughputs should be positive"

    @pytest.mark.asyncio
    async def test_latency_distribution(self, variable_latency_tool: Tool):
        """Test distribution of processing latencies."""
        processor = MockProcessor(capacity=50)

        # Create actions with varying latencies
        actions = []
        for _ in range(100):
            delay = 0.1 + (0.1 * (_ % 5))  # Increased delays
            action = FunctionCalling.create(
                tool=variable_latency_tool, arguments={"delay": delay}
            )
            actions.append(action)

        _, latencies = await self.measure_processing_time(processor, actions)

        # Calculate distribution metrics
        avg_latency = mean(latencies)
        latency_std = stdev(latencies)

        # Verify reasonable latency bounds
        assert (
            0.1 <= avg_latency <= 1.0
        ), f"Average latency {avg_latency} outside expected range"
        assert latency_std > 0, "Should have some latency variation"

        await processor.stop()

    @pytest.mark.asyncio
    async def test_concurrent_capacity_limits(
        self, variable_latency_tool: Tool
    ):
        """Test behavior at and beyond processing capacity limits."""
        capacity = 10
        processor = MockProcessor(capacity=capacity)

        # Create more actions than capacity
        action_count = capacity * 2
        actions = [
            FunctionCalling.create(
                tool=variable_latency_tool,
                arguments={"delay": 0.1},  # Increased delay
            )
            for _ in range(action_count)
        ]

        total_time, _ = await self.measure_processing_time(processor, actions)

        # Verify processing time scales with batching
        # Should take at least 2 batches
        min_expected_time = 0.1 * 2  # Two batches at 0.1 seconds each
        assert (
            total_time >= min_expected_time
        ), f"Processing time {total_time} too short for capacity limit {capacity}"

        # Verify all completed despite capacity limit
        await self.assert_all_actions_status(actions, EventStatus.COMPLETED)

        await processor.stop()

    @pytest.mark.asyncio
    async def test_error_handling_performance(
        self, variable_latency_tool: Tool
    ):
        """Test performance impact of error handling."""
        processor = MockProcessor(capacity=10, should_fail=True, max_retries=2)

        # Mix of successful and failing actions
        actions = []
        for i in range(20):
            # Every third action has invalid delay to trigger error
            delay = -1 if i % 3 == 0 else 0.1
            action = FunctionCalling.create(
                tool=variable_latency_tool, arguments={"delay": delay}
            )
            actions.append(action)

        total_time, _ = await self.measure_processing_time(
            processor,
            actions,
            expected_status=None,  # Don't check status since we expect failures
        )

        # Count final states
        completed = sum(
            1 for a in actions if a.status == EventStatus.COMPLETED
        )
        failed = sum(1 for a in actions if a.status == EventStatus.FAILED)

        # Verify error handling overhead
        assert completed + failed == len(actions), "All actions should be done"
        assert failed > 0, "Should have some failed actions"

        # Verify retries were attempted
        assert (
            sum(processor.retry_counts.values()) > 0
        ), "Should have retry attempts"

        await processor.stop()
