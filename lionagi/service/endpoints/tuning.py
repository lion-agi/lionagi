# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional

from pydantic import Field, validator

from .base import APICalling, EndPoint, EndpointConfig


class TuningEndpointConfig(EndpointConfig):
    """Configuration for model tuning endpoints.

    Extends EndpointConfig with tuning-specific parameters.

    Attributes:
        max_epochs (int): Maximum training epochs (1-1000)
        batch_size (int): Training batch size (1-512)
        learning_rate (float): Learning rate for optimization (1e-6 to 1.0)
        validation_split (float): Fraction of data for validation (0.0-1.0)
    """

    max_epochs: int = Field(
        default=100,
        gt=0,
        le=1000,
        description="Maximum number of training epochs",
    )
    batch_size: int = Field(
        default=32,
        gt=0,
        le=512,
        description="Number of samples per training batch",
    )
    learning_rate: float = Field(
        default=1e-4,
        gt=1e-6,
        le=1.0,
        description="Learning rate for optimization",
    )
    validation_split: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Fraction of data used for validation",
    )

    @validator("validation_split")
    def validate_split(cls, v):
        if v >= 1.0:
            raise ValueError("Validation split must be less than 1.0")
        return v


class TuningEndPoint(EndPoint):
    """Endpoint for model fine-tuning operations.

    Provides methods for training, validation and optimization.
    """

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.config = TuningEndpointConfig(**config)

    async def _invoke(self, payload: dict, headers: dict, **kwargs) -> Any:
        """Executes the tuning operation.

        Args:
            payload (dict): Training configuration and data
            headers (dict): Request headers
            **kwargs: Additional parameters

        Returns:
            dict: Training results and metrics

        Raises:
            ValueError: If payload or headers are invalid
            RuntimeError: If the API request fails
        """
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")

        required_fields = {"training_data", "model_config"}
        if not all(field in payload for field in required_fields):
            raise ValueError(f"Payload must contain fields: {required_fields}")

        if not headers.get("Authorization"):
            raise ValueError("Authorization header is required")

        try:
            response = await super()._invoke(payload, headers, **kwargs)

            # Validate response format
            if not isinstance(response, dict):
                raise ValueError(
                    "Invalid response format: expected dictionary"
                )

            required_response_fields = {"metrics", "best_model"}
            if not all(
                field in response for field in required_response_fields
            ):
                raise ValueError(
                    f"Response missing required fields: {required_response_fields}"
                )

            return response

        except Exception as e:
            raise RuntimeError(f"Tuning request failed: {str(e)}")


from typing import Dict, List, Optional, Union

from pydantic import Field, validator


class TuningEvent(APICalling):
    """Tracks a model tuning operation.

    Extends APICalling with training metrics and result tracking.

    Attributes:
        metrics (dict): Training metrics history with loss/accuracy values
        best_model (dict): Best model state and configuration
    """

    metrics: dict[str, list[float]] = Field(
        default_factory=dict, description="Training metrics history"
    )
    best_model: dict[str, int | dict] | None = Field(
        default=None, description="Best model state and configuration"
    )

    @validator("metrics")
    def validate_metrics(cls, v):
        if not all(isinstance(vals, list) for vals in v.values()):
            raise ValueError("Metrics must contain lists of numeric values")
        if not all(
            isinstance(x, (int, float)) for vals in v.values() for x in vals
        ):
            raise ValueError("Metric values must be numeric")
        return v

    @validator("best_model")
    def validate_best_model(cls, v):
        if v is not None:
            if "epoch" not in v:
                raise ValueError("Best model must contain 'epoch' field")
            if not isinstance(v["epoch"], int):
                raise ValueError("Epoch must be an integer")
        return v

    async def invoke(self) -> None:
        """Executes the tuning operation and tracks results."""
        try:
            await super().invoke()
            if self.execution.response:
                metrics = self.execution.response.get("metrics")
                best_model = self.execution.response.get("best_model")

                if metrics is not None:
                    self.metrics = metrics
                if best_model is not None:
                    self.best_model = best_model
        except Exception as e:
            raise RuntimeError(f"Failed to execute tuning operation: {str(e)}")
