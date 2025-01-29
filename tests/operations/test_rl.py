# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock

import pytest

from lionagi import Branch, iModel
from lionagi.operations.rl import (
    Experience,
    OptimizationMode,
    RLSystem,
    TuningConfig,
)


@pytest.fixture
def mock_branch():
    """Create a mock branch for testing"""
    mock_model = iModel(provider="openai", model="gpt-4o")
    return Branch(name="TestBranch", chat_model=mock_model)


@pytest.fixture
def training_data():
    """Sample training data"""
    return [
        {"prompt": "Test prompt 1", "target": "Expected response 1"},
        {"prompt": "Test prompt 2", "target": "Expected response 2"},
    ]


@pytest.mark.asyncio
async def test_rl_config():
    """Test RL configuration initialization"""
    config = TuningConfig(
        mode=OptimizationMode.HYBRID, learning_rate=1e-5, max_steps=100
    )

    assert config.mode == OptimizationMode.HYBRID
    assert config.learning_rate == 1e-5
    assert config.max_steps == 100


@pytest.mark.asyncio
async def test_experience_creation():
    """Test Experience object creation"""
    exp = Experience(
        prompt="test prompt",
        response="test response",
        reward=0.5,
        metadata={"test": "data"},
    )

    assert exp.prompt == "test prompt"
    assert exp.response == "test response"
    assert exp.reward == 0.5
    assert exp.metadata["test"] == "data"


@pytest.mark.asyncio
async def test_rl_system_initialization(mock_branch):
    """Test RLSystem initialization"""
    config = TuningConfig(mode=OptimizationMode.HYBRID)
    system = RLSystem(tuning_config=config)

    assert system.tuning_config.mode == OptimizationMode.HYBRID
    assert system._current_step == 0
    assert system._best_reward == float("-inf")


@pytest.mark.asyncio
async def test_synthetic_data_generation(mock_branch, training_data):
    """Test synthetic data generation"""
    config = TuningConfig(mode=OptimizationMode.SYNTHETIC_DATA)
    system = RLSystem(tuning_config=config)

    results = await system.train(
        branch=mock_branch, initial_examples=training_data, max_steps=1
    )

    assert isinstance(results, dict)
    assert "steps" in results
    assert "eval_results" in results


@pytest.mark.asyncio
async def test_parameter_tuning(mock_branch, training_data):
    """Test parameter tuning"""
    config = TuningConfig(
        mode=OptimizationMode.PARAMETER_TUNING, max_steps=1, batch_size=2
    )
    system = RLSystem(tuning_config=config)

    results = await system.train(
        branch=mock_branch, initial_examples=training_data
    )

    assert isinstance(results, dict)
    assert results["steps"] > 0


@pytest.mark.asyncio
async def test_hybrid_optimization(mock_branch, training_data):
    """Test hybrid optimization mode"""
    config = TuningConfig(
        mode=OptimizationMode.HYBRID,
        max_steps=1,
        batch_size=2,
        target_reward=0.9,
    )
    system = RLSystem(tuning_config=config)

    results = await system.train(
        branch=mock_branch,
        initial_examples=training_data,
        eval_examples=training_data,  # Use same data for testing
    )

    assert isinstance(results, dict)
    assert "final_metrics" in results
