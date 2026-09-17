from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.entities import Tender, Bid, Vendor, VendorRelationship, Project, Contract, Inspection, QualityRecord, Complaint, MaintenanceRecord

def evaluate_award_concentration(vendor: Vendor, peer_vendors: List[Vendor]) -> Optional[Dict[str, Any]]:
    # High win rate check
    if vendor.win_rate >= 0.70 and vendor.total_contracts >= 3:
        avg_peer_win_rate = sum(v.win_rate for v in peer_vendors) / max(len(peer_vendors), 1)
        return {
            "category": "PROCUREMENT",
            "title": f"High Award Concentration ({int(vendor.win_rate * 100)}% Win Rate)",
            "description": f"Vendor has won {int(vendor.win_rate * 100)}% of comparable tenders ({vendor.total_contracts} awards), substantially above peer baseline ({int(avg_peer_win_rate * 100)}%).",
            "severity": "CRITICAL" if vendor.win_rate >= 0.85 else "HIGH",
            "confidence": 94.0,
            "benchmark": f"Peer category average: {int(avg_peer_win_rate * 100)}% win rate",
            "score": min(100.0, vendor.win_rate * 100.0)
        }
    return None

def evaluate_price_anomaly(winning_bid: float, comparable_median: float, historical_median: float) -> Optional[Dict[str, Any]]:
    if comparable_median <= 0:
        return None
    deviation_pct = ((winning_bid - comparable_median) / comparable_median) * 100.0
    if deviation_pct >= 12.0:
        severity = "CRITICAL" if deviation_pct >= 25.0 else ("HIGH" if deviation_pct >= 15.0 else "MEDIUM")
        return {
            "category": "PRICE",
            "title": f"Elevated Bid Pricing (+{deviation_pct:.1f}% vs Benchmark)",
            "description": f"Winning bid amount is {deviation_pct:.1f}% higher than the comparable peer median for similar specifications.",
            "severity": severity,
            "confidence": 91.0,
            "benchmark": f"Comparable peer median: ₹{comparable_median:,.2f} | Historical median: ₹{historical_median:,.2f}",
            "score": min(100.0, 50.0 + deviation_pct * 1.5)
        }
    return None

def evaluate_vendor_relationships(vendor_id: int, db: Session, tender_bidders: List[int]) -> Optional[Dict[str, Any]]:
    relationships = db.query(VendorRelationship).filter(
        (VendorRelationship.source_vendor_id == vendor_id) | 
        (VendorRelationship.target_vendor_id == vendor_id)
    ).all()
    
    co_bidding_related = []
    for rel in relationships:
        other_id = rel.target_vendor_id if rel.source_vendor_id == vendor_id else rel.source_vendor_id
        if other_id in tender_bidders:
            co_bidding_related.append(rel)
            
    if co_bidding_related:
        primary = co_bidding_related[0]
        other_vendor = primary.target_vendor if primary.source_vendor_id == vendor_id else primary.source_vendor
        rel_type_label = primary.relationship_type.replace('_', ' ').title()
        return {
            "category": "NETWORK",
            "title": f"Connected Entity Co-Bidding ({rel_type_label})",
            "description": f"Winning vendor shares a documented {rel_type_label} with participating bidder '{other_vendor.name}' ({primary.entity_name or 'verified link'}).",
            "severity": "CRITICAL" if "DIRECTOR" in primary.relationship_type or "SUBSIDIARY" in primary.relationship_type else "HIGH",
            "confidence": 95.0,
            "benchmark": f"Documented entity link: {primary.evidence_details or 'Corporate registry record'}",
            "score": 88.0
        }
    elif relationships:
        return {
            "category": "NETWORK",
            "title": "Documented Inter-Vendor Corporate Ties",
            "description": f"Vendor maintains {len(relationships)} documented relationship ties (directors/addresses) across regional contracting entities.",
            "severity": "MEDIUM",
            "confidence": 85.0,
            "benchmark": "Entity relationship registry analysis",
            "score": 60.0
        }
    return None

def evaluate_bid_patterns(bids: List[Bid]) -> Optional[Dict[str, Any]]:
    if len(bids) >= 2:
        sorted_bids = sorted(bids, key=lambda b: b.bid_amount)
        # Check suspicious margin between 1st and 2nd
        if len(sorted_bids) >= 2:
            gap = ((sorted_bids[1].bid_amount - sorted_bids[0].bid_amount) / sorted_bids[0].bid_amount) * 100.0
            if 0.0 < gap <= 1.2:
                return {
                    "category": "PROCUREMENT",
                    "title": f"Suspicious Bid Clustering (Margin: {gap:.2f}%)",
                    "description": f"Runner-up bid was within {gap:.2f}% of winning bid, indicating potential coordinated non-competitive pricing.",
                    "severity": "HIGH",
                    "confidence": 88.0,
                    "benchmark": "Peer tender average margin: 6.8%",
                    "score": 75.0
                }
    return None

def evaluate_project_execution(project: Optional[Project]) -> Optional[Dict[str, Any]]:
    if not project:
        return None
    delay_pct = (project.delay_days / max(project.planned_duration_days, 1)) * 100.0
    cost_overrun = project.cost_overrun_pct
    
    if delay_pct >= 25.0 or project.delay_days >= 60:
        return {
            "category": "EXECUTION",
            "title": f"Substantial Project Delay (+{project.delay_days} Days / +{delay_pct:.1f}%)",
            "description": f"Project execution exceeded planned duration ({project.planned_duration_days} days) by {project.delay_days} days ({project.actual_duration_days} total days).",
            "severity": "CRITICAL" if delay_pct >= 50.0 else "HIGH",
            "confidence": 96.0,
            "benchmark": f"Planned: {project.planned_duration_days} days | Actual: {project.actual_duration_days} days",
            "score": min(100.0, 50.0 + delay_pct * 0.8)
        }
    return None

def evaluate_quality(project: Optional[Project], db: Session) -> Optional[Dict[str, Any]]:
    if not project:
        return None
    inspections = db.query(Inspection).filter(Inspection.project_id == project.id).all()
    failed_or_defects = [i for i in inspections if i.result in ["FAILED", "MAJOR_DEFECTS", "MINOR_DEFECTS"]]
    qual_records = db.query(QualityRecord).filter(QualityRecord.project_id == project.id).all()
    
    if failed_or_defects or qual_records:
        worst = "CRITICAL" if any(i.result == "FAILED" or q.severity == "CRITICAL" for i in failed_or_defects for q in qual_records) else "HIGH"
        details = qual_records[0].description if qual_records else failed_or_defects[0].specification_deviations or "Inspection findings recorded"
        return {
            "category": "QUALITY",
            "title": "Post-Award Specification & Quality Defects",
            "description": f"Physical inspections logged quality non-compliance: {details}",
            "severity": worst,
            "confidence": 92.0,
            "benchmark": f"{len(failed_or_defects)} inspection flags and {len(qual_records)} defect logs",
            "score": 85.0 if worst == "CRITICAL" else 70.0
        }
    return None

def evaluate_citizen_feedback(project: Optional[Project], db: Session) -> Optional[Dict[str, Any]]:
    if not project:
        return None
    complaints = db.query(Complaint).filter(
        Complaint.project_id == project.id,
        Complaint.status.in_(["VERIFIED", "INCLUDED_IN_ANALYTICS"])
    ).all()
    
    count = len(complaints)
    if count >= 5:
        return {
            "category": "PUBLIC_FEEDBACK",
            "title": f"High Citizen Complaint Volume ({count} Verified Reports)",
            "description": f"Citizens have submitted {count} verified on-site reports documenting defects, safety hazards, and physical degradation.",
            "severity": "CRITICAL" if count >= 20 else "HIGH",
            "confidence": 93.0,
            "benchmark": f"Regional category threshold: 3.5 complaints | Actual: {count} verified reports",
            "score": min(100.0, 40.0 + count * 1.5)
        }
    elif count >= 1:
        return {
            "category": "PUBLIC_FEEDBACK",
            "title": f"Isolated Citizen Feedback ({count} Report)",
            "description": f"A single verified citizen report was filed. Low investigative influence without multi-signal corroboration.",
            "severity": "LOW",
            "confidence": 80.0,
            "benchmark": f"Actual: {count} report",
            "score": 35.0
        }
    return None

def evaluate_maintenance(project: Optional[Project], db: Session) -> Optional[Dict[str, Any]]:
    if not project:
        return None
    records = db.query(MaintenanceRecord).filter(MaintenanceRecord.project_id == project.id).all()
    if not records:
        return None
    total_cost = sum(r.cost for r in records)
    max_ratio = max(r.benchmark_cost_ratio for r in records)
    
    if max_ratio >= 1.7:
        return {
            "category": "MAINTENANCE",
            "title": f"Elevated Lifecycle Maintenance Cost ({max_ratio:.1f}× Benchmark)",
            "description": f"Post-construction maintenance expenditures (₹{total_cost:,.2f}) are {max_ratio:.1f}× the expected regional lifecycle baseline.",
            "severity": "CRITICAL" if max_ratio >= 2.2 else "HIGH",
            "confidence": 90.0,
            "benchmark": f"Peer lifecycle benchmark: 1.0× | Observed: {max_ratio:.1f}×",
            "score": min(100.0, max_ratio * 40.0)
        }
    return None
