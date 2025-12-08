"""
Integration tests for providers status endpoint - optimized
"""

import pytest
from unittest.mock import patch


@patch('app.storage.repositories.ProviderStateRepository.get')
@patch('app.storage.repositories.ModelRateLimitsRepository.get_all')
@patch('app.monitoring.tracker.UsageTracker.get_provider_stats')
def test_providers_status(mock_get_stats, mock_rate_limits, mock_provider_state, test_client, auth_headers):
    """Test providers status endpoint with all database calls mocked"""
    # Mock all database/usage tracker calls
    mock_provider_state.return_value = None
    mock_rate_limits.return_value = []
    mock_get_stats.return_value = {"requests": 0, "tokens": 0, "errors": 0, "rate_limit_hits": 0, "time_window": 3600000}
    
    assert test_client.get("/api/v1/providers/status").status_code in [401, 403]
    
    response = test_client.get("/api/v1/providers/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data and isinstance(data["providers"], list)
    if len(data["providers"]) > 0:
        p = data["providers"][0]
        assert all(k in p for k in ["name", "healthy", "available", "rateLimitRemaining"])

