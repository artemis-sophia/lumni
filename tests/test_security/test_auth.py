"""
Security tests for authentication and authorization
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_api_key_validation(test_client, api_key):
    """Test that API key validation works correctly"""
    # Test with valid API key
    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "messages": [{"role": "user", "content": "test"}]
        }
    )
    # Should not be 401 (might be 400/422 for validation, but not auth error)
    assert response.status_code != 401


def test_invalid_api_key_rejected(test_client):
    """Test that invalid API keys are rejected"""
    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": "Bearer invalid-key"},
        json={
            "messages": [{"role": "user", "content": "test"}]
        }
    )
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]["error"] or \
           "AUTHENTICATION_ERROR" in response.json()["detail"].get("code", "")


def test_missing_api_key_rejected(test_client):
    """Test that requests without API key are rejected"""
    response = test_client.post(
        "/api/v1/chat",
        json={
            "messages": [{"role": "user", "content": "test"}]
        }
    )
    assert response.status_code in [401, 403]


def test_api_key_timing_attack_prevention(test_client, api_key):
    """Test that API key comparison uses constant-time comparison"""
    import time
    
    # Test with correct key
    start = time.time()
    response1 = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "messages": [{"role": "user", "content": "test"}]
        }
    )
    time_correct = time.time() - start
    
    # Test with incorrect key (similar length)
    start = time.time()
    response2 = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": "Bearer " + "x" * len(api_key)},
        json={
            "messages": [{"role": "user", "content": "test"}]
        }
    )
    time_incorrect = time.time() - start
    
    # Timing should be similar (constant-time comparison)
    # Allow some variance but should be close
    time_diff = abs(time_correct - time_incorrect)
    assert time_diff < 0.1  # Should be within 100ms (accounting for network variance)

