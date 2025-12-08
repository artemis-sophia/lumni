"""
Academic Task Classification System
Implements task classification based on academic research frameworks.
Classifies tasks as "fast" or "powerful" based on multiple factors.
"""

from typing import Literal
from dataclasses import dataclass
from app.api.v1.schemas import ChatRequest


@dataclass
class TaskComplexity:
    """Task complexity analysis"""
    complexity: Literal['simple', 'moderate', 'complex']
    token_intensity: Literal['low', 'medium', 'high']
    criticality: Literal['non-critical', 'important', 'critical']
    time_sensitivity: Literal['low', 'medium', 'high']


@dataclass
class TaskClassification:
    """Task classification result"""
    task_type: Literal['fast', 'powerful']
    confidence: float  # 0-1, confidence in classification
    factors: dict[str, float]


def classify_task(request: ChatRequest) -> TaskClassification:
    """Classify a task based on request characteristics"""
    complexity = analyze_complexity(request)
    factors = calculate_factors(request, complexity)

    # Determine task type based on weighted factors
    fast_score = calculate_fast_score(factors)
    powerful_score = calculate_powerful_score(factors)

    task_type = 'fast' if fast_score > powerful_score else 'powerful'
    confidence = abs(fast_score - powerful_score) / max(fast_score, powerful_score) if max(fast_score, powerful_score) > 0 else 0.0

    return TaskClassification(
        task_type=task_type,
        confidence=min(confidence, 1.0),
        factors=factors
    )


def analyze_complexity(request: ChatRequest) -> TaskComplexity:
    """Analyze task complexity from request"""
    total_length = sum(len(msg.content) for msg in request.messages)
    avg_length = total_length / len(request.messages) if request.messages else 0
    max_length = max((len(msg.content) for msg in request.messages), default=0)

    # Complexity based on message characteristics
    complexity: Literal['simple', 'moderate', 'complex'] = 'simple'
    if max_length > 2000 or len(request.messages) > 5:
        complexity = 'complex'
    elif avg_length > 500 or len(request.messages) > 2:
        complexity = 'moderate'

    # Token intensity
    token_intensity: Literal['low', 'medium', 'high'] = 'low'
    if total_length > 5000:
        token_intensity = 'high'
    elif total_length > 1000:
        token_intensity = 'medium'

    # Criticality (default to non-critical, can be overridden)
    criticality: Literal['non-critical', 'important', 'critical'] = 'non-critical'

    # Time sensitivity (default to medium for interactive)
    time_sensitivity: Literal['low', 'medium', 'high'] = 'medium'

    return TaskComplexity(
        complexity=complexity,
        token_intensity=token_intensity,
        criticality=criticality,
        time_sensitivity=time_sensitivity
    )


def calculate_factors(
    request: ChatRequest,
    complexity: TaskComplexity
) -> dict[str, float]:
    """Calculate classification factors"""
    import re

    has_system_message = any(msg.role == 'system' for msg in request.messages)
    has_code_blocks = any('```' in msg.content for msg in request.messages)
    has_complex_keywords = any(
        re.search(
            r'\b(reason|analyze|complex|critical|important|detailed|comprehensive|strategic|planning)\b',
            msg.content,
            re.IGNORECASE
        )
        for msg in request.messages
    )
    has_long_messages = any(len(msg.content) > 2000 for msg in request.messages)

    return {
        'complexity': 1.0 if complexity.complexity == 'complex' else (0.5 if complexity.complexity == 'moderate' else 0.0),
        'tokenIntensity': 1.0 if complexity.token_intensity == 'high' else (0.5 if complexity.token_intensity == 'medium' else 0.0),
        'criticality': 1.0 if complexity.criticality == 'critical' else (0.5 if complexity.criticality == 'important' else 0.0),
        'timeSensitivity': 1.0 if complexity.time_sensitivity == 'high' else (0.5 if complexity.time_sensitivity == 'medium' else 0.0),
        'keywordMatch': 1.0 if has_complex_keywords else 0.0,
        'systemMessage': 1.0 if has_system_message else 0.0,
        'codeBlocks': 1.0 if has_code_blocks else 0.0,
    }


def calculate_fast_score(factors: dict[str, float]) -> float:
    """Calculate score for "fast" model selection"""
    # Fast models favor:
    # - High token intensity (weight: 0.3)
    # - Low complexity (weight: 0.2)
    # - Low criticality (weight: 0.1)
    # - High time sensitivity (weight: 0.2)
    # - Code blocks (weight: 0.2) - token-intensive but often simple

    return (
        factors['tokenIntensity'] * 0.3 +
        (1 - factors['complexity']) * 0.2 +
        (1 - factors['criticality']) * 0.1 +
        factors['timeSensitivity'] * 0.2 +
        factors['codeBlocks'] * 0.2
    )


def calculate_powerful_score(factors: dict[str, float]) -> float:
    """Calculate score for "powerful" model selection"""
    # Powerful models favor:
    # - High complexity (weight: 0.3)
    # - High criticality (weight: 0.2)
    # - Complex keywords (weight: 0.2)
    # - System messages (weight: 0.2)
    # - Long messages (weight: 0.1)

    return (
        factors['complexity'] * 0.3 +
        factors['criticality'] * 0.2 +
        factors['keywordMatch'] * 0.2 +
        factors['systemMessage'] * 0.2 +
        (0.1 if factors['complexity'] > 0.5 else 0.0)
    )


def get_recommended_category(request: ChatRequest) -> Literal['fast', 'powerful']:
    """Get recommended model category for a task"""
    # If explicitly specified, use that
    if request.task_type and request.task_type != 'auto':
        return request.task_type  # type: ignore

    # Auto-detect
    classification = classify_task(request)
    return classification.task_type


def get_detailed_classification(request: ChatRequest) -> TaskClassification:
    """Get classification with detailed information"""
    return classify_task(request)

