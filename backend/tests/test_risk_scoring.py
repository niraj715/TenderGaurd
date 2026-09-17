import pytest
from backend.app.anomaly.c_indicators import AnomalyIndicatorEngine

def test_priority_score_range_and_tiers():
    # Empty indicators
    engine = AnomalyIndicatorEngine([], [], [], [], [], [])
    score, tier = engine._calculate_priority_score([])
    assert 0.0 <= score <= 100.0
    assert tier == "Low"

    # Single moderate indicator
    score, tier = engine._calculate_priority_score([{
        "indicator_code": "C1",
        "severity": 0.70,
        "confidence": 0.85
    }])
    assert 30.0 <= score <= 60.0

    # Multi-family convergence
    multi = [
        {"indicator_code": "C1", "severity": 0.85, "confidence": 0.95}, # Competition
        {"indicator_code": "C8", "severity": 0.85, "confidence": 0.95}, # Pricing
        {"indicator_code": "C17", "severity": 0.95, "confidence": 0.95}, # Relationship
    ]
    score_multi, tier_multi = engine._calculate_priority_score(multi)
    assert score_multi >= 70.0
    assert tier_multi in ("High", "Critical")
