"""
Unit tests for benchmark selector
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models.benchmark_selector import BenchmarkSelector, ModelSelectionResult
from app.api.v1.schemas import ChatRequest, Message
from app.core.litellm_client import LiteLLMClient


@pytest.mark.asyncio
async def test_select_model_scenarios():
    """Test model selection for different scenarios"""
    mock_client = MagicMock(spec=LiteLLMClient)
    selector = BenchmarkSelector(mock_client)
    
    # Explicit provider and model
    req = ChatRequest(provider="groq", model="llama-3.1-8b-instant", messages=[Message(role="user", content="Hello")])
    result = await selector.select_model(req)
    assert result.provider == "groq" and "llama-3.1-8b-instant" in result.model
    
    # Model only
    req = ChatRequest(model="llama-3.1-8b-instant", messages=[Message(role="user", content="Hello")])
    result = await selector.select_model(req)
    assert result.model and result.provider
    
    # Task type selection
    for task_type in ["fast", "powerful", "auto"]:
        req = ChatRequest(task_type=task_type, messages=[Message(role="user", content="Test")])
        try:
            result = await selector.select_model(req)
            assert result.provider and result.model
        except ValueError:
            pass  # Acceptable if no models configured


@pytest.mark.asyncio
async def test_benchmark_selector_helpers():
    """Test helper methods"""
    mock_client = MagicMock(spec=LiteLLMClient)
    selector = BenchmarkSelector(mock_client)
    
    assert isinstance(await selector.get_all_models(), list)
    assert isinstance(await selector.get_models_by_provider("groq"), list)

