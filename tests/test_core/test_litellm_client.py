"""
Unit tests for LiteLLM client
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.litellm_client import LiteLLMClient
from app.api.v1.schemas import ChatRequest, Message


@pytest.mark.asyncio
async def test_litellm_client_initialization():
    """Test LiteLLM client initialization"""
    client = LiteLLMClient(config_path="./litellm_config.yaml")
    
    assert client.config_path == "./litellm_config.yaml"
    assert client.circuit_breaker is not None


@pytest.mark.asyncio
@patch('app.core.litellm_client.litellm.acompletion')
async def test_litellm_client_chat_success(mock_acompletion):
    """Test successful chat completion"""
    # Mock LiteLLM response
    mock_response = MagicMock()
    mock_response.id = "test-id"
    mock_response.object = "chat.completion"
    mock_response.created = 1234567890
    mock_response.model = "gpt-3.5-turbo"
    mock_response.choices = [
        MagicMock(
            index=0,
            message=MagicMock(role="assistant", content="Hello!"),
            finish_reason="stop"
        )
    ]
    mock_response.usage = MagicMock(
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15
    )
    
    mock_acompletion.return_value = mock_response
    
    client = LiteLLMClient(config_path="./litellm_config.yaml")
    
    request = ChatRequest(
        model="gpt-3.5-turbo",
        provider="openai",
        messages=[Message(role="user", content="Hello")]
    )
    
    response = await client.chat(request)
    
    assert response.id == "test-id"
    assert response.model == "gpt-3.5-turbo"
    assert len(response.choices) == 1
    assert response.choices[0].message.content == "Hello!"
    assert response.usage.total_tokens == 15


@pytest.mark.asyncio
@patch('app.core.litellm_client.litellm.acompletion')
async def test_litellm_client_chat_with_proxy(mock_acompletion):
    """Test chat completion with proxy"""
    mock_response = MagicMock()
    mock_response.id = "test-id"
    mock_response.object = "chat.completion"
    mock_response.created = 1234567890
    mock_response.model = "gpt-3.5-turbo"
    mock_response.choices = [
        MagicMock(
            index=0,
            message=MagicMock(role="assistant", content="Hello!"),
            finish_reason="stop"
        )
    ]
    mock_response.usage = MagicMock(
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15
    )
    
    mock_acompletion.return_value = mock_response
    
    client = LiteLLMClient(config_path="./litellm_config.yaml")
    
    request = ChatRequest(
        model="gpt-3.5-turbo",
        provider="openai",
        messages=[Message(role="user", content="Hello")]
    )
    
    proxy = "http://proxy.example.com:8080"
    
    response = await client.chat(request, proxy=proxy)
    
    # Verify proxy was used (check if extra_headers or env vars were set)
    assert response.id == "test-id"
    # Note: Actual proxy verification would require checking env vars or request params


@pytest.mark.asyncio
@patch('app.core.litellm_client.litellm.acompletion')
async def test_litellm_client_chat_rate_limit_error(mock_acompletion):
    """Test handling of rate limit errors"""
    from app.utils.exceptions import RateLimitError
    
    # Mock rate limit error
    mock_acompletion.side_effect = Exception("rate limit exceeded")
    
    client = LiteLLMClient(config_path="./litellm_config.yaml")
    
    request = ChatRequest(
        model="gpt-3.5-turbo",
        provider="openai",
        messages=[Message(role="user", content="Hello")]
    )
    
    with pytest.raises(RateLimitError):
        await client.chat(request)


@pytest.mark.asyncio
@patch('app.core.litellm_client.litellm.acompletion')
async def test_litellm_client_chat_provider_error(mock_acompletion):
    """Test handling of provider errors"""
    from app.utils.exceptions import ProviderError
    
    # Mock provider error
    mock_acompletion.side_effect = Exception("Provider unavailable")
    
    client = LiteLLMClient(config_path="./litellm_config.yaml")
    
    request = ChatRequest(
        model="gpt-3.5-turbo",
        provider="openai",
        messages=[Message(role="user", content="Hello")]
    )
    
    with pytest.raises(ProviderError):
        await client.chat(request)


@pytest.mark.asyncio
async def test_litellm_client_get_available_models():
    """Test getting available models"""
    client = LiteLLMClient(config_path="./litellm_config.yaml")
    
    models = await client.get_available_models()
    
    # Should return a list (may be empty if config not found)
    assert isinstance(models, list)

