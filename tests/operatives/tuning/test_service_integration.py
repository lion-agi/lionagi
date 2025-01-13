from unittest.mock import AsyncMock, MagicMock

import pytest

from lionagi.service.endpoints.tuning import (
    TuningEndPoint,
    TuningEndpointConfig,
    TuningEvent,
)


@pytest.fixture
def mock_config():
    return {
        "max_epochs": 50,
        "batch_size": 16,
        "learning_rate": 2e-4,
        "validation_split": 0.1,
        "url": "https://api.example.com/tune",
        "model": "test-model",
    }


@pytest.fixture
def tuning_endpoint(mock_config):
    return TuningEndPoint(mock_config)


@pytest.fixture
def mock_response():
    return {
        "metrics": {
            "train_loss": [0.5, 0.3, 0.2],
            "val_loss": [0.6, 0.4, 0.3],
        },
        "best_model": {"epoch": 2, "params": {"weights": [0.1, 0.2, 0.3]}},
    }


class TestTuningEndpointConfig:
    def test_config_initialization(self, mock_config):
        config = TuningEndpointConfig(**mock_config)
        assert config.max_epochs == 50
        assert config.batch_size == 16
        assert config.learning_rate == 2e-4
        assert config.validation_split == 0.1

    def test_config_validation(self):
        with pytest.raises(ValueError):
            TuningEndpointConfig(
                max_epochs=-1,
                batch_size=16,
                learning_rate=1e-4,
                validation_split=0.2,
            )


class TestTuningEndPoint:
    async def test_invoke_calls_super(self, tuning_endpoint):
        tuning_endpoint._invoke = AsyncMock()
        payload = {"data": "test"}
        headers = {"Authorization": "Bearer test"}

        await tuning_endpoint._invoke(payload, headers)
        tuning_endpoint._invoke.assert_called_once_with(payload, headers)

    def test_endpoint_initialization(self, mock_config):
        endpoint = TuningEndPoint(mock_config)
        assert isinstance(endpoint.config, TuningEndpointConfig)
        assert endpoint.config.max_epochs == mock_config["max_epochs"]


class TestTuningEvent:
    @pytest.fixture
    def tuning_event(self):
        return TuningEvent(
            payload={"data": "test"},
            headers={"Authorization": "Bearer test"},
            endpoint=MagicMock(),
        )

    async def test_invoke_updates_metrics(self, tuning_event, mock_response):
        tuning_event.execution = MagicMock()
        tuning_event.execution.response = mock_response

        await tuning_event.invoke()
        assert tuning_event.metrics == mock_response["metrics"]
        assert tuning_event.best_model == mock_response["best_model"]

    async def test_invoke_handles_empty_response(self, tuning_event):
        tuning_event.execution = MagicMock()
        tuning_event.execution.response = None

        await tuning_event.invoke()
        assert tuning_event.metrics == {}
        assert tuning_event.best_model is None

    async def test_invoke_with_error(self, tuning_event):
        tuning_event.execution = MagicMock()
        tuning_event.execution.response = {"error": "Training failed"}

        await tuning_event.invoke()
        assert tuning_event.metrics == {}
