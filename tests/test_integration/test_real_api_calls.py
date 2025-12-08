"""
Integration tests with REAL API calls
These tests use actual API keys and make real requests to providers.
Run separately: pytest tests/test_integration/test_real_api_calls.py -v
"""

import pytest
import os
from dotenv import load_dotenv
from app.core.litellm_client import LiteLLMClient
from app.api.v1.schemas import ChatRequest, Message
from app.models.benchmark_selector import BenchmarkSelector

# Load environment variables
load_dotenv()


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set - skipping real API test"
)
@pytest.mark.asyncio
async def test_real_litellm_call_groq():
    """Test real LiteLLM call to Groq"""
    client = LiteLLMClient(config_path="./litellm_config.yaml")
    
    request = ChatRequest(
        model="groq/llama-3.1-8b-instant",
        provider="groq",
        messages=[Message(role="user", content="Say 'test' in one word")]
    )
    
    response = await client.chat(request)
    
    assert response.id is not None
    assert response.model is not None
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert "test" in response.choices[0].message.content.lower()


@pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY"),
    reason="DEEPSEEK_API_KEY not set - skipping real API test"
)
@pytest.mark.asyncio
async def test_real_litellm_call_deepseek():
    """Test real LiteLLM call to DeepSeek"""
    client = LiteLLMClient(config_path="./litellm_config.yaml")
    
    request = ChatRequest(
        model="deepseek/deepseek-chat",
        provider="deepseek",
        messages=[Message(role="user", content="Say hello")]
    )
    
    response = await client.chat(request)
    
    assert response.id is not None
    assert response.model is not None
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set - skipping real API test"
)
@pytest.mark.asyncio
async def test_real_benchmark_selector():
    """Test benchmark selector with real LiteLLM"""
    client = LiteLLMClient(config_path="./litellm_config.yaml")
    selector = BenchmarkSelector(client)
    
    request = ChatRequest(
        provider="groq",
        model="llama-3.1-8b-instant",
        messages=[Message(role="user", content="Test")]
    )
    
    selection = await selector.select_model(request)
    
    assert selection.provider == "groq"
    assert "llama" in selection.model.lower()
    assert selection.reason is not None


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set - skipping real API test"
)
@pytest.mark.asyncio
async def test_real_chat_endpoint_via_client():
    """Test chat endpoint logic with real API (without FastAPI test client)"""
    from app.core.litellm_client import LiteLLMClient
    from app.core.portkey_client import PortkeyClient
    from app.models.benchmark_selector import BenchmarkSelector
    from app.models.task_classifier import get_detailed_classification
    from app.config import load_config
    from app.config.pricing import calculate_cost
    
    config = load_config()
    litellm_client = LiteLLMClient(config.litellm.config_path)
    portkey_client = PortkeyClient(
        api_key=config.portkey.api_key,
        environment=config.portkey.environment,
        virtual_key=config.portkey.virtual_key,
        config=config.portkey.config
    )
    benchmark_selector = BenchmarkSelector(litellm_client)
    
    # Create request
    chat_request = ChatRequest(
        messages=[Message(role="user", content="Say 'integration test'")],
        provider="groq",
        model="llama-3.1-8b-instant"
    )
    
    # Classify task
    classification = get_detailed_classification(chat_request)
    assert classification.task_type in ['fast', 'powerful']
    
    # Select model
    selection = await benchmark_selector.select_model(chat_request)
    assert selection.provider is not None
    assert selection.model is not None
    
    # Execute via LiteLLM
    async def completion_fn():
        selected_request = ChatRequest(
            model=selection.model,
            provider=selection.provider,
            messages=chat_request.messages,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
            stream=chat_request.stream
        )
        return await litellm_client.chat(selected_request)
    
    # Track with Portkey
    response = await portkey_client.track_completion(chat_request, completion_fn)
    
    # Verify response
    assert response.id is not None
    assert response.model is not None
    assert len(response.choices) > 0
    assert response.usage.total_tokens > 0
    
    # Calculate cost
    cost = calculate_cost(
        response.provider,
        response.model,
        response.usage.prompt_tokens,
        response.usage.completion_tokens
    )
    assert cost >= 0

