"""
Unit tests for task classifier
"""

import pytest
from app.models.task_classifier import (
    classify_task,
    analyze_complexity,
    calculate_factors,
    get_recommended_category
)
from app.api.v1.schemas import ChatRequest, Message


def test_classify_task_types():
    """Test classification for different task types"""
    # Simple task
    simple = classify_task(ChatRequest(messages=[Message(role="user", content="What is 2+2?")]))
    assert simple.task_type in ['fast', 'powerful'] and 0.0 <= simple.confidence <= 1.0
    assert 'complexity' in simple.factors
    
    # Complex task
    complex_task = classify_task(ChatRequest(messages=[
        Message(role="user", content="Write a comprehensive research paper on quantum computing.")
    ]))
    assert complex_task.task_type in ['fast', 'powerful']
    
    # Code generation
    code = classify_task(ChatRequest(messages=[
        Message(role="user", content="Write a Python function for binary search tree.")
    ]))
    assert code.task_type in ['fast', 'powerful']


def test_analyze_complexity():
    """Test complexity analysis"""
    simple = analyze_complexity(ChatRequest(messages=[Message(role="user", content="Hello")]))
    assert all(attr in ['simple', 'moderate', 'complex', 'low', 'medium', 'high', 'non-critical', 'important', 'critical'] 
               for attr in [simple.complexity, simple.token_intensity, simple.criticality, simple.time_sensitivity])
    
    complex_req = analyze_complexity(ChatRequest(messages=[Message(role="user", content="Analysis " * 100)]))
    assert complex_req.complexity in ['simple', 'moderate', 'complex']


def test_calculate_factors():
    """Test factor calculation"""
    request = ChatRequest(
        messages=[
            Message(role="user", content="Explain quantum mechanics")
        ]
    )
    
    complexity = analyze_complexity(request)
    factors = calculate_factors(request, complexity)
    
    assert isinstance(factors, dict)
    assert len(factors) > 0
    # All factors should be numeric
    for key, value in factors.items():
        assert isinstance(value, (int, float))


def test_get_recommended_category():
    """Test getting recommended category"""
    request = ChatRequest(
        messages=[
            Message(role="user", content="Quick question")
        ]
    )
    
    category = get_recommended_category(request)
    
    assert category in ['fast', 'powerful']


def test_classify_edge_cases():
    """Test classification edge cases"""
    # Explicit task type
    request = ChatRequest(task_type="fast", messages=[Message(role="user", content="Test")])
    assert classify_task(request).task_type in ['fast', 'powerful']
    
    # Empty messages
    request = ChatRequest(messages=[])
    result = classify_task(request)
    assert result.task_type in ['fast', 'powerful'] and 0.0 <= result.confidence <= 1.0

