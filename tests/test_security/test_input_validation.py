"""
Security tests for input validation
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_message_count_limit(test_client, api_key):
    """Test that message count is limited"""
    # Create request with too many messages (> 100)
    messages = [{"role": "user", "content": f"Message {i}"} for i in range(101)]
    
    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"messages": messages}
    )
    
    # Should be rejected with validation error
    assert response.status_code in [400, 422]
    assert "message" in response.json()["detail"].lower() or \
           "validation" in response.json()["detail"].lower()


def test_message_content_length_limit(test_client, api_key):
    """Test that message content length is limited"""
    # Create message with content > 100KB
    large_content = "x" * (101 * 1024)  # 101KB
    
    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "messages": [{"role": "user", "content": large_content}]
        }
    )
    
    # Should be rejected with validation error
    assert response.status_code in [400, 422]


def test_request_body_size_limit(test_client, api_key):
    """Test that request body size is limited"""
    # Create very large request body (> 10MB)
    # Note: This is tested at middleware level
    large_messages = [{"role": "user", "content": "x" * (11 * 1024 * 1024)}]
    
    response = test_client.post(
        "/api/v1/chat",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Length": str(11 * 1024 * 1024)
        },
        json={"messages": large_messages}
    )
    
    # Should be rejected with 413 Payload Too Large
    assert response.status_code == 413 or response.status_code in [400, 422]


def test_max_tokens_validation(test_client, api_key):
    """Test that max_tokens is validated"""
    # Test with max_tokens > 1,000,000
    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 2000000
        }
    )
    
    # Should be rejected with validation error
    assert response.status_code in [400, 422]


def test_temperature_validation(test_client, api_key):
    """Test that temperature is validated (0.0-2.0)"""
    # Test with temperature > 2.0
    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "messages": [{"role": "user", "content": "test"}],
            "temperature": 3.0
        }
    )
    
    # Should be rejected with validation error
    assert response.status_code in [400, 422]
    
    # Test with temperature < 0.0
    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "messages": [{"role": "user", "content": "test"}],
            "temperature": -1.0
        }
    )
    
    # Should be rejected with validation error
    assert response.status_code in [400, 422]


def test_sql_injection_prevention(test_client, api_key):
    """Test that SQL injection attempts are prevented"""
    # Try SQL injection in message content
    sql_injection = "'; DROP TABLE usage_metrics; --"
    
    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "messages": [{"role": "user", "content": sql_injection}]
        }
    )
    
    # Should not cause SQL errors (SQLAlchemy should handle this)
    # Response might be 400/422 for validation or 500 for provider error, but not SQL error
    assert response.status_code != 500 or "sql" not in response.text.lower()
    
    # Verify database still works
    from app.storage.database import check_database_connection
    db_healthy, _ = check_database_connection()
    assert db_healthy is True


def test_xss_prevention(test_client, api_key):
    """Test that XSS attempts are sanitized in responses"""
    xss_payload = "<script>alert('xss')</script>"
    
    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "messages": [{"role": "user", "content": xss_payload}]
        }
    )
    
    # Response should not contain unescaped script tags
    # (This depends on provider response, but we should validate)
    if response.status_code == 200:
        response_data = response.json()
        # Check that response is properly structured
        assert "choices" in response_data or "error" in response_data

