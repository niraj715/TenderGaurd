from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.database import get_db
from backend.app.core.security import require_investigator
from backend.app.models.entities import (
    Investigation, Tender, Vendor, Award, RiskSignal, InvestigationNote,
    Complaint, Project, User, Inspection, QualityRecord, MaintenanceRecord
)

router = APIRouter(prefix="/alerts", tags=["Alerts & Investigation Queue"])

def resolve_investigation(id_or_code: str, db: Session) -> Optional[Investigation]:
    if str(id_or_code).isdigit():
        inv = db.query(Investigation).filter(Investigation.id == int(id_or_code)).first()
        if inv:
            return inv
        inv = db.query(Investigation).filter(Investigation.tender_id == f"T{int(id_or_code):03d}").first()
        if inv:
            return inv
    inv = db.query(Investigation).filter(Investigation.case_code == str(id_or_code)).first()
    if inv:
        return inv
    inv = db.query(Investigation).filter(Investigation.tender_id == str(id_or_code)).first()
    if inv:
        return inv
    return None

@router.get("")
def get_alerts(
    priority: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    query = db.query(Investigation)

    if priority and priority.lower() != "all":
        p_upper = priority.upper()
        if p_upper == "MEDIUM":
            query = query.filter(Investigation.priority_tier.in_(["Medium", "Moderate", "Elevated", "medium", "moderate", "elevated"]))
        else:
            query = query.filter(Investigation.priority_tier.ilike(priority))
    if status and status.lower() != "all":
        query = query.filter(Investigation.status.ilike(status))
    if category and category.lower() != "all":
        query = query.join(Tender).filter(Tender.category.ilike(f"%{category}%"))

    # Priority queue: sort by priority_score descending
    alerts = query.order_by(Investigation.priority_score.desc()).all()

    results = []
    for a in alerts:
        t = a.tender
        award = t.award if t else None
        winner = award.vendor if (award and award.vendor) else None
        signals = a.signals

        main_sig = signals[0].title if signals else "Standard Monitoring"
        conf = round(max([s.confidence for s in signals] or [0.85]), 2)

        # Normalize priority tier
        tier_upper = a.priority_tier.upper()
        if tier_upper in ("MODERATE", "ELEVATED"):
            tier_upper = "MEDIUM"

        results.append({
            "id": a.id,
            "case_code": a.case_code,
            "tender_id": t.id if t else a.id,
            "tender_code": t.tender_id if t else f"T{a.id:03d}",
            "vendor_id": winner.id if winner else 1,
            "vendor_code": winner.vendor_id if winner else "V001",
            "project_id": t.id if t else a.id,
            "project_name": t.tender_title if t else f"Tender {a.tender_id}",
            "vendor_name": winner.vendor_name if winner else "BuildRight Infra",
            "priority_score": a.priority_score,
            "priority_tier": tier_upper,
            "status": a.status.upper(),
            "assigned_investigator_name": a.assigned_investigator or "Sarah Chen",
            "main_signal": main_sig,
            "procurement_risk": round(min(0.95, a.priority_score / 100 * 0.9), 2),
            "network_risk": round(min(0.95, a.priority_score / 100 * 0.85), 2),
            "price_risk": round(min(0.95, a.priority_score / 100 * 0.88), 2),
            "execution_risk": 0.45,
            "quality_risk": 0.50,
            "feedback_risk": 0.40,
            "maintenance_risk": 0.35,
            "confidence_score": conf,
            "ai_summary": a.summary_narrative,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else None,
            "updated_at": a.updated_at.strftime("%Y-%m-%d %H:%M:%S") if a.updated_at else None,
            "signals_count": len(signals)
        })

    return results

@router.get("/{alert_id}")
def get_alert_detail(
    alert_id: str,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    a = resolve_investigation(alert_id, db)
    if not a:
        raise HTTPException(status_code=404, detail=f"Case {alert_id} not found")

    t = a.tender
    award = t.award if t else None
    winner = award.vendor if (award and award.vendor) else None
    contract = t.contract if t else None
    signals = a.signals
    notes = a.notes

    # Linked Project
    proj = None
    if t:
        if t.projects:
            proj = t.projects[0]
        else:
            proj = db.query(Project).filter(Project.tender_id == t.tender_id).first()

    signals_resp = []
    for s in signals:
        signals_resp.append({
            "id": s.id,
            "signal_category": s.signal_category,
            "indicator_code": s.indicator_code,
            "title": s.title,
            "description": s.description,
            "severity": "CRITICAL" if s.severity >= 0.80 else ("HIGH" if s.severity >= 0.70 else "MEDIUM"),
            "confidence": s.confidence,
            "peer_benchmark_info": f"Peer Group Category: {t.category if t else 'Civil Infrastructure'}",
            "supporting_evidence_json": s.evidence_json
        })

    notes_resp = []
    for n in sorted(notes, key=lambda x: x.created_at, reverse=True):
        notes_resp.append({
            "id": n.id,
            "author_name": n.author_name,
            "note_text": n.note_text,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S") if n.created_at else None
        })

    complaints_list = []
    if t:
        comps = db.query(Complaint).filter(or_(Complaint.tender_id == t.tender_id, Complaint.project_id == (proj.id if proj else -1))).all()
        for c in comps:
            complaints_list.append({
                "id": c.id,
                "project_id": proj.id if proj else (t.id if t else 1),
                "tender_id": t.tender_id,
                "project_name": proj.name if proj else t.tender_title,
                "citizen_id": c.citizen_id,
                "citizen_name": c.citizen.name if c.citizen else "Citizen Auditor",
                "title": c.title,
                "description": c.description,
                "category": c.category,
                "rating": c.rating,
                "location": c.location,
                "status": c.status,
                "reviewer_credibility_weight": c.reviewer_credibility_weight,
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None,
                "media": []
            })

    # Inspections
    inspections_list = []
    if proj:
        for insp in proj.inspections:
            inspections_list.append({
                "id": insp.id,
                "project_id": proj.id,
                "inspection_date": insp.inspection_date.strftime("%Y-%m-%d") if insp.inspection_date else None,
                "inspector_name": insp.inspector_name,
                "inspector_agency": insp.inspector_agency,
                "result": insp.result,
                "specification_deviations": insp.specification_deviations,
                "notes": insp.notes
            })

    # Quality Records
    quality_list = []
    if proj:
        for q in proj.quality_records:
            quality_list.append({
                "id": q.id,
                "project_id": proj.id,
                "defect_category": q.defect_category,
                "severity": q.severity,
                "description": q.description,
                "detected_date": q.detected_date.strftime("%Y-%m-%d") if q.detected_date else None,
                "resolved": q.resolved
            })

    # Maintenance Records
    maintenance_list = []
    if proj:
        for m in proj.maintenance_records:
            maintenance_list.append({
                "id": m.id,
                "project_id": proj.id,
                "maintenance_date": m.maintenance_date.strftime("%Y-%m-%d") if m.maintenance_date else None,
                "cost": m.cost,
                "vendor_id": m.vendor_id,
                "maintenance_type": m.maintenance_type,
                "benchmark_cost_ratio": m.benchmark_cost_ratio,
                "description": m.description
            })

    # Build Dynamic Chronological Timeline
    timeline_events = []
    if t:
        if t.publication_date:
            timeline_events.append({
                "date": t.publication_date.strftime("%Y-%m-%d"),
                "timestamp": t.publication_date.isoformat(),
                "title": "Tender Notice Published",
                "category": "PROCUREMENT",
                "status": "COMPLETED",
                "description": f"Published by {t.buyer_name} for estimated value of ₹{t.estimated_value_inr:,.2f} ({t.procurement_method})."
            })
        if t.submission_deadline:
            timeline_events.append({
                "date": t.submission_deadline.strftime("%Y-%m-%d"),
                "timestamp": t.submission_deadline.isoformat(),
                "title": "Bidding Closed",
                "category": "PROCUREMENT",
                "status": "COMPLETED",
                "description": f"Bids submission closed with {len(t.bids)} competitive bid(s) received."
            })
        if t.technical_evaluation_date:
            timeline_events.append({
                "date": t.technical_evaluation_date.strftime("%Y-%m-%d"),
                "timestamp": t.technical_evaluation_date.isoformat(),
                "title": "Technical Evaluation",
                "category": "EVALUATION",
                "status": "COMPLETED",
                "description": "Technical responsiveness criteria evaluated and verified against bid specifications."
            })
        if t.financial_evaluation_date:
            timeline_events.append({
                "date": t.financial_evaluation_date.strftime("%Y-%m-%d"),
                "timestamp": t.financial_evaluation_date.isoformat(),
                "title": "Financial Bid Opening",
                "category": "EVALUATION",
                "status": "COMPLETED",
                "description": f"Financial bids opened; {winner.vendor_name if winner else 'Vendor'} identified as lowest responsive bidder."
            })
        if award and award.award_date:
            timeline_events.append({
                "date": award.award_date.strftime("%Y-%m-%d"),
                "timestamp": award.award_date.isoformat(),
                "title": "Contract Awarded",
                "category": "AWARD",
                "status": "COMPLETED",
                "description": f"Officially awarded to {winner.vendor_name if winner else 'Vendor'} at contract sum of ₹{award.awarded_amount_inr:,.2f}."
            })
    if contract:
        if contract.start_date:
            timeline_events.append({
                "date": contract.start_date.strftime("%Y-%m-%d"),
                "timestamp": contract.start_date.isoformat(),
                "title": "Execution Commenced",
                "category": "EXECUTION",
                "status": "COMPLETED",
                "description": f"Site mobilization and construction works initiated in {t.location if t else 'Site'}."
            })
        if contract.planned_end_date:
            is_delayed = contract.actual_duration_days > contract.planned_duration_days
            timeline_events.append({
                "date": contract.planned_end_date.strftime("%Y-%m-%d"),
                "timestamp": contract.planned_end_date.isoformat(),
                "title": "Scheduled Milestone Target",
                "category": "MILESTONE",
                "status": "DELAYED" if is_delayed else "ON_TRACK",
                "description": f"Original planned duration: {contract.planned_duration_days} days. {'Milestone exceeded scheduled baseline.' if is_delayed else 'Completed within timeline.'}"
            })
        if contract.actual_end_date:
            timeline_events.append({
                "date": contract.actual_end_date.strftime("%Y-%m-%d"),
                "timestamp": contract.actual_end_date.isoformat(),
                "title": "Project Handover & Completion",
                "category": "EXECUTION",
                "status": contract.completion_status,
                "description": f"Contract concluded with status '{contract.completion_status}' after {contract.actual_duration_days} days."
            })

    # Add Inspections to timeline
    for insp in inspections_list:
        if insp["inspection_date"]:
            timeline_events.append({
                "date": insp["inspection_date"],
                "timestamp": insp["inspection_date"],
                "title": f"Site Inspection: {insp['result']}",
                "category": "QUALITY",
                "status": insp["result"],
                "description": f"Inspection by {insp['inspector_name']} ({insp['inspector_agency']}). {insp['specification_deviations'] or insp['notes'] or ''}"
            })

    # Add Complaints to timeline
    for comp in complaints_list:
        c_date = comp["created_at"].split()[0] if comp["created_at"] else None
        if c_date:
            timeline_events.append({
                "date": c_date,
                "timestamp": comp["created_at"],
                "title": f"Citizen Audit: {comp['title'][:40]}",
                "category": "CITIZEN",
                "status": comp["status"],
                "description": f"Reported by {comp['citizen_name']} (Rating: {comp['rating']}/5): {comp['description']}"
            })

    # Add Maintenance to timeline
    for m in maintenance_list:
        if m["maintenance_date"]:
            timeline_events.append({
                "date": m["maintenance_date"],
                "timestamp": m["maintenance_date"],
                "title": f"Maintenance: {m['maintenance_type']}",
                "category": "MAINTENANCE",
                "status": "COMPLETED",
                "description": f"Maintenance expense ₹{m['cost']:,.2f} ({m['benchmark_cost_ratio']}x benchmark ratio). {m['description'] or ''}"
            })

    # Add Investigation Alert Created to timeline
    if a.created_at:
        timeline_events.append({
            "date": a.created_at.strftime("%Y-%m-%d"),
            "timestamp": a.created_at.isoformat(),
            "title": f"Anomaly Alert Flagged ({a.priority_tier.upper()})",
            "category": "INVESTIGATION",
            "status": a.status,
            "description": f"Automated Anomaly Engine computed priority score {a.priority_score}/100 based on {len(signals)} risk indicators."
        })

    # Sort chronological
    timeline_events.sort(key=lambda x: x["date"] or "")

    tier_upper = a.priority_tier.upper()
    if tier_upper in ("MODERATE", "ELEVATED"):
        tier_upper = "MEDIUM"

    bids_resp = []
    if t:
        for b in t.bids:
            bids_resp.append({
                "id": b.id,
                "tender_id": t.id,
                "vendor_id": b.vendor.id if b.vendor else 1,
                "vendor_code": b.vendor_id,
                "vendor_name": b.vendor.vendor_name if b.vendor else "Unknown",
                "bid_amount": b.bid_amount_inr,
                "submission_time": b.submission_timestamp.strftime("%Y-%m-%d %H:%M:%S") if b.submission_timestamp else None,
                "rank": 1 if b.is_winner else 2,
                "is_winning": b.is_winner,
                "technical_score": b.technical_score,
                "pricing_deviation_pct": round(((b.bid_amount_inr - t.estimated_value_inr) / t.estimated_value_inr) * 100, 2)
            })
        bids_resp.sort(key=lambda x: (not x["is_winning"], x["bid_amount"]))

    return {
        "id": a.id,
        "case_code": a.case_code,
        "tender_id": t.id if t else a.id,
        "tender_code": t.tender_id if t else f"T{a.id:03d}",
        "vendor_id": winner.id if winner else 1,
        "vendor_code": winner.vendor_id if winner else "V001",
        "project_id": proj.id if proj else (t.id if t else a.id),
        "project_name": proj.name if proj else (t.tender_title if t else f"Tender {a.tender_id}"),
        "vendor_name": winner.vendor_name if winner else "BuildRight Infra",
        "priority_score": a.priority_score,
        "priority_tier": tier_upper,
        "status": a.status.upper(),
        "assigned_investigator_name": a.assigned_investigator or "Sarah Chen",
        "main_signal": signals[0].title if signals else "Standard Monitoring",
        "procurement_risk": round(min(0.95, a.priority_score / 100 * 0.9), 2),
        "network_risk": round(min(0.95, a.priority_score / 100 * 0.85), 2),
        "price_risk": round(min(0.95, a.priority_score / 100 * 0.88), 2),
        "execution_risk": 0.45,
        "quality_risk": 0.50,
        "feedback_risk": 0.40,
        "maintenance_risk": 0.35,
        "confidence_score": round(max([s.confidence for s in signals] or [0.85]), 2),
        "ai_summary": a.summary_narrative,
        "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else None,
        "updated_at": a.updated_at.strftime("%Y-%m-%d %H:%M:%S") if a.updated_at else None,
        "signals_count": len(signals),
        "signals": signals_resp,
        "notes": notes_resp,
        "complaints": complaints_list,
        "inspections": inspections_list,
        "quality_records": quality_list,
        "maintenance": maintenance_list,
        "timeline": timeline_events,
        "project_detail": {
            "id": proj.id if proj else (t.id if t else 1),
            "contract_id": int(contract.contract_id.replace("C", "")) if contract else 1,
            "name": proj.name if proj else (t.tender_title if t else "Infrastructure Project"),
            "description": proj.description if proj else f"Public procurement project in {t.location if t else 'Solan'}, {t.state if t else 'HP'}",
            "category": proj.category if proj else (t.category if t else "Civil Infrastructure"),
            "department": proj.department if proj else (t.buyer_name if t else "PWD"),
            "location_name": proj.location_name if proj else (t.location if t else "Solan"),
            "planned_duration_days": contract.planned_duration_days if contract else (proj.planned_duration_days if proj else 180),
            "actual_duration_days": contract.actual_duration_days if contract else (proj.actual_duration_days if proj else 180),
            "delay_days": max(0, ((contract.actual_duration_days if contract else 180) - (contract.planned_duration_days if contract else 180))),
            "planned_cost": t.estimated_value_inr if t else 10000000.0,
            "actual_cost": award.awarded_amount_inr if award else 10000000.0,
            "cost_overrun_pct": round(((award.awarded_amount_inr - t.estimated_value_inr) / t.estimated_value_inr) * 100, 2) if (award and t) else 0.0,
            "execution_status": contract.completion_status if contract else (proj.execution_status if proj else "COMPLETED"),
            "quality_status": proj.quality_status if proj else ("ACTION_REQUIRED" if a.priority_score >= 70 else "SATISFACTORY"),
            "vendor_id": winner.id if winner else 1,
            "vendor_name": winner.vendor_name if winner else "BuildRight Infra",
            "created_at": t.publication_date.strftime("%Y-%m-%d") if (t and t.publication_date) else None
        },
        "vendor_detail": {
            "id": winner.id if winner else 1,
            "name": winner.vendor_name if winner else "BuildRight Infra",
            "registration_number": winner.registration_number if winner else "REG-1001",
            "category": winner.industry_category if winner else "Infrastructure",
            "win_rate": winner.win_rate if winner else 0.35,
            "total_contracts": winner.total_contracts if winner else 24,
            "total_contract_value": winner.total_contract_value if winner else 150000000.0,
            "avg_delay_days": winner.avg_delay_days if winner else 42.0,
            "quality_score": 82.5,
            "complaint_rate": 0.08,
            "maintenance_cost_ratio": 1.25,
            "risk_level": winner.risk_level if winner else "HIGH",
            "city": winner.city if winner else "Solan",
            "state": winner.state if winner else "HP"
        } if winner else None,
        "tender_detail": {
            "id": t.id if t else 1,
            "tender_code": t.tender_id if t else "T001",
            "title": t.tender_title if t else "Tender",
            "department": t.buyer_name if t else "PWD",
            "category": t.category if t else "Civil Infrastructure",
            "estimated_value": t.estimated_value_inr if t else 10000000.0,
            "publication_date": t.publication_date.strftime("%Y-%m-%d") if (t and t.publication_date) else None,
            "submission_deadline": t.submission_deadline.strftime("%Y-%m-%d") if (t and t.submission_deadline) else None,
            "status": t.status if t else "AWARDED",
            "winning_vendor_id": winner.id if winner else 1,
            "winning_vendor_name": winner.vendor_name if winner else "BuildRight Infra",
            "winning_bid_amount": award.awarded_amount_inr if award else 10000000.0,
            "location": t.location if t else "Solan",
            "bids": bids_resp
        } if t else None
    }
