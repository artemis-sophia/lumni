"""
Academic Task Classification System
Uses spaCy for NLP-based text analysis with custom rules wrapper.
Classifies tasks as "fast" or "powerful" based on multiple factors.
"""

from typing import Literal
from dataclasses import dataclass
import re
import spacy
from app.api.v1.schemas import ChatRequest
from app.utils.logger import Logger

logger = Logger("TaskClassifier")

# Load spaCy model (lazy loading)
_nlp = None


def get_nlp():
    """Get or load spaCy NLP model"""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warn("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
            # Fallback to basic English model if available
            try:
                _nlp = spacy.load("en_core_web_lg")
            except OSError:
                logger.warn("Falling back to basic regex-based analysis")
                _nlp = None
    return _nlp


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
    """Classify a task based on request characteristics using spaCy NLP"""
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
    """Analyze task complexity from request using spaCy NLP"""
    nlp = get_nlp()
    
    # Combine all messages for analysis
    combined_text = " ".join(msg.content for msg in request.messages)
    total_length = len(combined_text)
    avg_length = total_length / len(request.messages) if request.messages else 0
    max_length = max((len(msg.content) for msg in request.messages), default=0)

    # Use spaCy for advanced analysis if available
    if nlp and combined_text:
        doc = nlp(combined_text)
        
        # Analyze sentence complexity
        sentence_count = len(list(doc.sents))
        avg_sentence_length = len(doc) / sentence_count if sentence_count > 0 else 0
        
        # Count named entities (indicates complexity)
        entity_count = len(doc.ents)
        
        # Analyze POS tags for complexity indicators
        complex_pos_tags = ['NOUN', 'VERB', 'ADJ', 'ADV']
        complex_pos_count = sum(1 for token in doc if token.pos_ in complex_pos_tags)
        complexity_ratio = complex_pos_count / len(doc) if len(doc) > 0 else 0
        
        # Determine complexity based on NLP features
        if max_length > 2000 or len(request.messages) > 5 or avg_sentence_length > 25 or entity_count > 5:
            complexity: Literal['simple', 'moderate', 'complex'] = 'complex'
        elif avg_length > 500 or len(request.messages) > 2 or avg_sentence_length > 15 or entity_count > 2:
            complexity = 'moderate'
        else:
            complexity = 'simple'
    else:
        # Fallback to basic analysis
        if max_length > 2000 or len(request.messages) > 5:
            complexity = 'complex'
        elif avg_length > 500 or len(request.messages) > 2:
            complexity = 'moderate'
        else:
            complexity = 'simple'

    # Token intensity
    token_intensity: Literal['low', 'medium', 'high'] = 'low'
    if total_length > 5000:
        token_intensity = 'high'
    elif total_length > 1000:
        token_intensity = 'medium'

    # Criticality detection using spaCy NER
    criticality: Literal['non-critical', 'important', 'critical'] = 'non-critical'
    if nlp and combined_text:
        doc = nlp(combined_text)
        # Look for criticality indicators in entities and keywords
        critical_keywords = ['critical', 'urgent', 'important', 'essential', 'vital', 'crucial']
        critical_entities = ['PERSON', 'ORG', 'GPE']  # People, organizations, locations often indicate importance
        
        has_critical_keywords = any(
            keyword.lower() in token.text.lower() 
            for keyword in critical_keywords 
            for token in doc
        )
        has_important_entities = len([e for e in doc.ents if e.label_ in critical_entities]) > 3
        
        if has_critical_keywords or has_important_entities:
            criticality = 'critical' if has_critical_keywords else 'important'
    else:
        # Fallback regex-based detection
        critical_pattern = re.compile(
            r'\b(critical|urgent|important|essential|vital|crucial)\b',
            re.IGNORECASE
        )
        if critical_pattern.search(combined_text):
            criticality = 'critical'

    # Time sensitivity (default to medium for interactive)
    time_sensitivity: Literal['low', 'medium', 'high'] = 'medium'
    if nlp and combined_text:
        doc = nlp(combined_text)
        time_keywords = ['urgent', 'asap', 'immediately', 'quick', 'fast', 'now']
        has_time_keywords = any(
            keyword.lower() in token.text.lower()
            for keyword in time_keywords
            for token in doc
        )
        if has_time_keywords:
            time_sensitivity = 'high'

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
    """Calculate classification factors using spaCy NLP"""
    nlp = get_nlp()
    combined_text = " ".join(msg.content for msg in request.messages)

    has_system_message = any(msg.role == 'system' for msg in request.messages)
    has_code_blocks = any('```' in msg.content for msg in request.messages)
    
    # Use spaCy for keyword detection if available
    if nlp and combined_text:
        doc = nlp(combined_text)
        
        # Complex keywords using spaCy lemmatization
        complex_lemmas = {'reason', 'analyze', 'complex', 'critical', 'important', 
                         'detailed', 'comprehensive', 'strategic', 'planning',
                         'evaluate', 'assess', 'examine', 'investigate'}
        has_complex_keywords = any(
            token.lemma_.lower() in complex_lemmas
            for token in doc
        )
        
        # Detect long messages using spaCy sentence analysis
        has_long_messages = any(
            len(list(nlp(msg.content).sents)) > 3 or len(msg.content) > 2000
            for msg in request.messages
        )
    else:
        # Fallback regex-based detection
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
