# lionagi/strategies/types.py

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class SystemMetrics(BaseModel):
    """Metrics for strategy selection and monitoring."""

    current_system_load: float = Field(
        default=0.0,
        description="Current system load (0.0 to 1.0, or more if beyond capacity)",
    )
    memory_usage: float = Field(
        default=0.0, description="Memory usage as fraction (0.0 to 1.0)"
    )
    historical_success_rate: float = Field(
        default=1.0, description="Historical success rate (0.0 to 1.0)"
    )
    historical_latency: float = Field(
        default=0.0, description="Historical average latency in seconds"
    )


class ExecutionProgress(BaseModel):
    """Tracks execution progress across strategy switches."""

    current_step: int = Field(default=0)
    total_steps: int = Field(default=0)
    completed_items: int = Field(default=0)
    failed_items: int = Field(default=0)
    checkpoints: dict[str, Any] = Field(default_factory=dict)


class StrategyScoringFactors(BaseModel):
    """Scoring factors for strategy selection."""

    concurrency_factor: float = Field(
        default=0.0, description="Score based on concurrency potential"
    )
    memory_factor: float = Field(
        default=0.0, description="Score based on memory usage"
    )
    performance_factor: float = Field(
        default=0.0, description="Score based on historical performance"
    )


class StrategyScore(BaseModel):
    """Final score for a strategy."""

    strategy_name: str
    score: float
    factors: dict[str, float]
    constraints: dict[str, Any]


class ModelAnalysis(BaseModel):
    """Analysis of model characteristics."""

    field_count: int = Field(
        default=0, description="Number of fields in model"
    )
    dependent_fields: list[str] = Field(
        default_factory=list, description="Fields with dependencies"
    )
    validation_complexity: float = Field(
        default=0.0, description="Complexity score for validation"
    )
    concurrent_safety: float = Field(
        default=1.0, description="Safety score for concurrent execution"
    )
    memory_footprint: float = Field(
        default=0.0, description="Estimated memory footprint"
    )

    class Config:
        arbitrary_types_allowed = True


class StrategyParams(BaseModel):
    """Parameters for strategy execution."""

    concurrency_limit: int = Field(
        default=4, description="Maximum concurrent operations"
    )
    chunk_size: int = Field(
        default=10, description="Size of chunks for chunked execution"
    )
    retry_limit: int = Field(default=3, description="Maximum retry attempts")
    timeout: float = Field(
        default=30.0, description="Operation timeout in seconds"
    )
