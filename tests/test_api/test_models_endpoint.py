"""
Integration tests for models endpoint - optimized
"""

import pytest


def test_models_endpoint_auth_and_response(test_client, auth_headers):
    """Test models endpoint auth and basic response"""
    # Test auth requirement
    assert test_client.get("/api/v1/models").status_code in [401, 403]
    
    # Test with auth
    response = test_client.get("/api/v1/models", headers=auth_headers)
    assert response.status_code == 200
    assert "models" in response.json()


def test_provider_models_endpoint(test_client, auth_headers):
    """Test provider-specific models endpoint"""
    response = test_client.get("/api/v1/models/groq", headers=auth_headers)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert data["provider"] == "groq" and "models" in data

