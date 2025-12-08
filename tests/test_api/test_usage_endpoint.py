"""
Integration tests for usage endpoint - optimized
"""

import pytest


def test_usage_endpoint(test_client, auth_headers):
    """Test usage endpoint auth and response"""
    assert test_client.get("/api/v1/usage").status_code in [401, 403]
    
    response = test_client.get("/api/v1/usage?window=3600000", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data and data["timeWindow"] == 3600000

