"""
Integration tests with REAL HTTP requests to running server
These tests require the server to be running: python3 -m uvicorn app.main:app --port 3000
Run: pytest tests/test_integration/test_real_http_endpoint.py -v
"""

import pytest
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:3000")
API_KEY = os.getenv("UNIFIED_API_KEY", "test-unified-api-key-12345")


@pytest.fixture(scope="module")
def server_available():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        pytest.skip("Server not running. Start with: python3 -m uvicorn app.main:app --port 3000")


def test_real_health_endpoint(server_available):
    """Test health endpoint with real server"""
    response = requests.get(f"{BASE_URL}/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set - skipping real API test"
)
def test_real_chat_endpoint_http(server_available):
    """Test chat endpoint with real HTTP request and real API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [{"role": "user", "content": "Say 'test' in one word"}],
        "provider": "groq",
        "model": "llama-3.1-8b-instant"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        headers=headers,
        json=data,
        timeout=30
    )
    
    assert response.status_code == 200, f"Request failed: {response.text[:200]}"
    result = response.json()
    
    assert "id" in result
    assert "model" in result
    assert "choices" in result
    assert len(result["choices"]) > 0
    assert "content" in result["choices"][0]["message"]
    assert "test" in result["choices"][0]["message"]["content"].lower()
    
    # Verify cost calculation
    if "cost" in result:
        assert result["cost"]["total"] >= 0


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set - skipping real API test"
)
def test_real_chat_endpoint_auto_selection(server_available):
    """Test chat endpoint with automatic model selection"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [{"role": "user", "content": "Hello"}],
        "task_type": "fast"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        headers=headers,
        json=data,
        timeout=30
    )
    
    assert response.status_code == 200, f"Request failed: {response.text[:200]}"
    result = response.json()
    
    assert "id" in result
    assert "model" in result
    assert "choices" in result
    assert len(result["choices"]) > 0


def test_real_models_endpoint(server_available):
    """Test models endpoint with real server"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/api/v1/models", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert isinstance(data["models"], list)


def test_real_usage_endpoint(server_available):
    """Test usage endpoint with real server"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/api/v1/usage", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "timeWindow" in data


def test_real_providers_status_endpoint(server_available):
    """Test providers status endpoint with real server"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/api/v1/providers/status", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert isinstance(data["providers"], list)

