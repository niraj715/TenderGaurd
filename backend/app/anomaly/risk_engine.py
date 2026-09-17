from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.entities import (
    Tender, Bid, Vendor, Project, Contract, Inspection,
    QualityRecord, Complaint, MaintenanceRecord, Alert, RiskSignal
)
from backend.app.anomaly.rules import (
    evaluate_award_concentration, evaluate_price_anomaly, evaluate_vendor_relationships,
    evaluate_bid_patterns, evaluate_project_execution, evaluate_quality,
    evaluate_citizen_feedback, evaluate_maintenance
)
from backend.app.anomaly.statistical import calculate_peer_cluster_statistics
from backend.app.anomaly.ml_model import ml_detector

def calculate_investigation_priority(
    tender: Tender,
    vendor: Vendor,
    project: Optional[Project],
    db: Session,
    peer_vendors: List[Vendor]
) -> Dict[str, Any]:
    """
    Calculates 0-100 Investigation Priority Score combining:
    - Procurement Risk (20%)
    - Vendor Network Risk (15%)
    - Price Risk (15%)
    - Execution Risk (15%)
    - Quality Risk (15%)
    - Public Feedback Risk (10%)
    - Maintenance Risk (10%)
    """
    signals: List[Dict[str, Any]] = []
    
    # 1. Procurement & Award Concentration
    procurement_signal = evaluate_award_concentration(vendor, peer_vendors)
    if procurement_signal:
        signals.append(procurement_signal)
    proc_score = procurement_signal["score"] if procurement_signal else 15.0
    
    # Bid patterns
    bids = db.query(Bid).filter(Bid.tender_id == tender.id).all()
    bid_pattern_signal = evaluate_bid_patterns(bids)
    if bid_pattern_signal:
        signals.append(bid_pattern_signal)
        proc_score = max(proc_score, bid_pattern_signal["score"])
        
    # 2. Price Risk & Benchmarking
    stats = calculate_peer_cluster_statistics(tender.category, db)
    comp_median = stats["bid_stats"]["median"]
    hist_median = comp_median * 0.95
    winning_bid = tender.winning_bid_amount or tender.estimated_value
    price_signal = evaluate_price_anomaly(winning_bid, comp_median, hist_median)
    if price_signal:
        signals.append(price_signal)
        price_score = price_signal["score"]
    else:
        price_score = 10.0
        
    # 3. Vendor Network Risk
    tender_bidder_ids = [b.vendor_id for b in bids]
    network_signal = evaluate_vendor_relationships(vendor.id, db, tender_bidder_ids)
    if network_signal:
        signals.append(network_signal)
        net_score = network_signal["score"]
    else:
        net_score = 10.0
        
    # 4. Project Execution Risk
    exec_signal = evaluate_project_execution(project)
    if exec_signal:
        signals.append(exec_signal)
        exec_score = exec_signal["score"]
    else:
        exec_score = 10.0
        
    # 5. Quality Risk
    qual_signal = evaluate_quality(project, db)
    if qual_signal:
        signals.append(qual_signal)
        qual_score = qual_signal["score"]
    else:
        qual_score = 10.0
        
    # 6. Citizen Feedback Risk
    feedback_signal = evaluate_citizen_feedback(project, db)
    if feedback_signal:
        signals.append(feedback_signal)
        feed_score = feedback_signal["score"]
    else:
        feed_score = 5.0
        
    # 7. Maintenance & Lifecycle Risk
    maint_signal = evaluate_maintenance(project, db)
    if maint_signal:
        signals.append(maint_signal)
        maint_score = maint_signal["score"]
    else:
        maint_score = 10.0

    # Weighted composite calculation
    base_priority = (
        settings.WEIGHT_PROCUREMENT * proc_score +
        settings.WEIGHT_VENDOR_NETWORK * net_score +
        settings.WEIGHT_PRICE * price_score +
        settings.WEIGHT_EXECUTION * exec_score +
        settings.WEIGHT_QUALITY * qual_score +
        settings.WEIGHT_PUBLIC_FEEDBACK * feed_score +
        settings.WEIGHT_MAINTENANCE * maint_score
    )

    # Multi-Signal Escalation (PRD Section 31):
    # Count severe signals (HIGH or CRITICAL)
    severe_signals = [s for s in signals if s.get("severity") in ["HIGH", "CRITICAL"]]
    critical_signals = [s for s in signals if s.get("severity") == "CRITICAL"]
    
    if len(severe_signals) >= 4 or len(critical_signals) >= 2:
        # Multi-signal convergence escalation
        priority_score = min(100.0, max(90.0, base_priority * 1.12))
    elif len(severe_signals) == 1 and not critical_signals:
        # Prevent false-alarm critical for single isolated signals
        priority_score = min(74.0, base_priority)
    else:
        priority_score = min(100.0, base_priority)

    priority_score = round(priority_score, 1)

    # Priority Tier assignment
    if priority_score >= settings.THRESHOLD_CRITICAL:
        tier = "CRITICAL"
    elif priority_score >= settings.THRESHOLD_HIGH:
        tier = "HIGH"
    elif priority_score >= settings.THRESHOLD_MEDIUM:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    # Main Signal summary
    if signals:
        top_signal = sorted(signals, key=lambda s: (0 if s["severity"]=="CRITICAL" else 1, -s["score"]))[0]
        main_signal = top_signal["title"]
    else:
        main_signal = "Normal procurement parameters observed"

    # Confidence calculation based on evidence corroboration
    confidence_score = round(min(98.0, 75.0 + (len(signals) * 3.5)), 1)

    return {
        "priority_score": priority_score,
        "priority_tier": tier,
        "main_signal": main_signal,
        "procurement_risk": round(proc_score, 1),
        "network_risk": round(net_score, 1),
        "price_risk": round(price_score, 1),
        "execution_risk": round(exec_score, 1),
        "quality_risk": round(qual_score, 1),
        "feedback_risk": round(feed_score, 1),
        "maintenance_risk": round(maint_score, 1),
        "confidence_score": confidence_score,
        "signals": signals
    }
