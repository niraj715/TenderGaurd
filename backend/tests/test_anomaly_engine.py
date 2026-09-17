import pytest
from backend.app.core.database import SessionLocal
from backend.app.models.entities import Alert, RiskSignal, Vendor, Project, Complaint

def test_acceptance_criteria_scenarios():
    db = SessionLocal()
    try:
        alerts = db.query(Alert).all()
        assert len(alerts) >= 50, "Expected at least 50 seeded investigation alerts"
        
        # Test Flagship Flagged Case (e.g. CASE-T001 with C1 Single Bidder)
        t1 = db.query(Alert).filter(Alert.case_code == "CASE-T001").first()
        assert t1 is not None
        assert t1.priority_tier in ["CRITICAL", "HIGH", "ELEVATED", "MODERATE", "Moderate"]
        assert t1.priority_score >= 40.0
        
        signals = [s.title for s in t1.signals]
        assert any("C1" in s or "Single Bidder" in s for s in signals), "Expected C1 Single Bidder signal on T001"
        
        # Test Clean Control Case (T040 clean control)
        t40 = db.query(Alert).filter(Alert.case_code == "CASE-T040").first()
        assert t40 is not None
        assert t40.priority_tier.upper() == "LOW", "Clean control must have LOW priority tier"
        assert t40.priority_score < 40.0
        
        # Test C7 Pricing Anomaly Case
        t5 = db.query(Alert).filter(Alert.case_code == "CASE-T005").first()
        assert t5 is not None
        t5_signals = [s.title for s in t5.signals]
        assert any("C7" in s or "Identical" in s for s in t5_signals), "Expected C7 pricing anomaly signal on T005"

        # Verify Complaints are present
        complaints_count = db.query(Complaint).count()
        assert complaints_count >= 5, "Expected at least 5 citizen complaints"
        
    finally:
        db.close()
