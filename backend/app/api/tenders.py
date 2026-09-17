from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.database import get_db
from backend.app.models.entities import (
    Tender, Bid, Vendor, Award, Contract, Investigation, RiskSignal,
    InvestigationNote, VendorRelationship, VendorTogetherParticipation
)
from backend.app.anomaly.c_indicators import AnomalyIndicatorEngine

router = APIRouter(prefix="/tenders", tags=["Tenders & Forensic Dossiers"])

def resolve_tender(tender_id_or_code: str, db: Session) -> Optional[Tender]:
    # Check by tender_id string (e.g. T001)
    t = db.query(Tender).filter(Tender.tender_id == str(tender_id_or_code)).first()
    if t:
        return t
    # Check by integer id
    if str(tender_id_or_code).isdigit():
        t = db.query(Tender).filter(Tender.id == int(tender_id_or_code)).first()
        if t:
            return t
        # Also try formatted T{idx:03d}
        t = db.query(Tender).filter(Tender.tender_id == f"T{int(tender_id_or_code):03d}").first()
        if t:
            return t
    return None

@router.get("")
def get_tenders(
    category: Optional[str] = None,
    buyer: Optional[str] = None,
    priority_tier: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    query = db.query(Tender)

    if category and category.lower() != "all":
        query = query.filter(Tender.category.ilike(f"%{category}%"))
    if buyer and buyer.lower() != "all":
        query = query.filter(or_(Tender.buyer_name.ilike(f"%{buyer}%"), Tender.buyer_id == buyer))
    if priority_tier and priority_tier.lower() != "all":
        query = query.join(Investigation).filter(Investigation.priority_tier.ilike(priority_tier))
    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            Tender.tender_title.ilike(s),
            Tender.tender_id.ilike(s),
            Tender.location.ilike(s),
            Tender.buyer_name.ilike(s)
        ))

    p = int(page.default) if hasattr(page, "default") else int(page)
    ps = int(page_size.default) if hasattr(page_size, "default") else int(page_size)
    total = query.count()
    tenders = query.order_by(Tender.id.asc()).offset((p - 1) * ps).limit(ps).all()

    items = []
    for t in tenders:
        award = t.award
        winner_id = award.winner_vendor_id if award else None
        winner_vendor = award.vendor if award else None
        inv = t.investigation

        items.append({
            "id": t.id,
            "tender_id": t.tender_id,
            "tender_code": t.tender_id,
            "title": t.tender_title,
            "category": t.category,
            "sub_category": t.sub_category,
            "buyer_id": t.buyer_id,
            "buyer_name": t.buyer_name,
            "location": t.location,
            "state": t.state,
            "estimated_value_inr": t.estimated_value_inr,
            "estimated_value": t.estimated_value_inr,
            "awarded_amount_inr": award.awarded_amount_inr if award else None,
            "awarded_value": award.awarded_amount_inr if award else None,
            "publication_date": t.publication_date.strftime("%Y-%m-%d %H:%M:%S") if t.publication_date else None,
            "submission_deadline": t.submission_deadline.strftime("%Y-%m-%d %H:%M:%S") if t.submission_deadline else None,
            "status": t.status,
            "bidders_count": len(t.bids),
            "winner_vendor_id": winner_id,
            "winner_vendor_name": winner_vendor.vendor_name if winner_vendor else None,
            "priority_score": inv.priority_score if inv else 12.0,
            "priority_tier": inv.priority_tier if inv else "Low",
            "signals_count": inv.signals_count if inv else 0
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }

@router.get("/categories")
def get_tender_categories(db: Session = Depends(get_db)) -> List[str]:
    cats = db.query(Tender.category).distinct().order_by(Tender.category.asc()).all()
    return [c[0] for c in cats if c[0]]

@router.get("/{tender_id}")
def get_tender(tender_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    t = resolve_tender(tender_id, db)
    if not t:
        raise HTTPException(status_code=404, detail=f"Tender {tender_id} not found")

    award = t.award
    contract = t.contract
    inv = t.investigation

    bids_list = []
    for b in t.bids:
        bids_list.append({
            "id": b.id,
            "bid_id": b.bid_id,
            "vendor_id": b.vendor_id,
            "vendor_name": b.vendor.vendor_name if b.vendor else "Unknown",
            "bid_amount_inr": b.bid_amount_inr,
            "bid_amount": b.bid_amount_inr,
            "submission_timestamp": b.submission_timestamp.strftime("%Y-%m-%d %H:%M:%S") if b.submission_timestamp else None,
            "bid_status": b.bid_status,
            "disqualification_reason": b.disqualification_reason,
            "technical_score": b.technical_score,
            "financial_score": b.financial_score,
            "is_winner": b.is_winner,
            "variance_from_estimate_pct": round(((b.bid_amount_inr - t.estimated_value_inr) / t.estimated_value_inr) * 100, 2)
        })

    # Sort bids: qualified by price ascending, then disqualified
    bids_list.sort(key=lambda x: (x["bid_status"] == "DISQUALIFIED", x["bid_amount_inr"]))

    return {
        "id": t.id,
        "tender_id": t.tender_id,
        "tender_code": t.tender_id,
        "title": t.tender_title,
        "tender_title": t.tender_title,
        "category": t.category,
        "sub_category": t.sub_category,
        "buyer_id": t.buyer_id,
        "buyer_name": t.buyer_name,
        "department": t.buyer_name,
        "location": t.location,
        "state": t.state,
        "estimated_value_inr": t.estimated_value_inr,
        "estimated_value": t.estimated_value_inr,
        "procurement_method": t.procurement_method,
        "award_criteria": t.award_criteria,
        "publication_date": t.publication_date.strftime("%Y-%m-%d %H:%M:%S") if t.publication_date else None,
        "submission_deadline": t.submission_deadline.strftime("%Y-%m-%d %H:%M:%S") if t.submission_deadline else None,
        "technical_evaluation_date": t.technical_evaluation_date.strftime("%Y-%m-%d") if t.technical_evaluation_date else None,
        "financial_evaluation_date": t.financial_evaluation_date.strftime("%Y-%m-%d") if t.financial_evaluation_date else None,
        "award_date": t.award_date.strftime("%Y-%m-%d") if t.award_date else None,
        "contract_duration_days": t.contract_duration_days,
        "status": t.status,
        "winner": {
            "vendor_id": award.winner_vendor_id if award else None,
            "vendor_name": award.vendor.vendor_name if (award and award.vendor) else None,
            "awarded_amount_inr": award.awarded_amount_inr if award else None,
            "awarded_date": award.award_date.strftime("%Y-%m-%d") if (award and award.award_date) else None,
            "award_reason": award.award_reason if award else None,
            "variance_from_estimate_pct": round(((award.awarded_amount_inr - t.estimated_value_inr) / t.estimated_value_inr) * 100, 2) if award else 0.0
        } if award else None,
        "contract": {
            "contract_id": contract.contract_id,
            "contract_value_inr": contract.contract_value_inr,
            "start_date": contract.start_date.strftime("%Y-%m-%d") if contract.start_date else None,
            "planned_end_date": contract.planned_end_date.strftime("%Y-%m-%d") if contract.planned_end_date else None,
            "actual_end_date": contract.actual_end_date.strftime("%Y-%m-%d") if contract.actual_end_date else None,
            "planned_duration_days": contract.planned_duration_days,
            "actual_duration_days": contract.actual_duration_days,
            "completion_status": contract.completion_status
        } if contract else None,
        "priority_score": inv.priority_score if inv else 12.0,
        "priority_tier": inv.priority_tier if inv else "Low",
        "signals_count": inv.signals_count if inv else 0,
        "bids": bids_list
    }

@router.get("/{tender_id}/bids")
def get_tender_bids(tender_id: str, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    t = resolve_tender(tender_id, db)
    if not t:
        raise HTTPException(status_code=404, detail=f"Tender {tender_id} not found")

    res = []
    for b in t.bids:
        res.append({
            "id": b.id,
            "bid_id": b.bid_id,
            "tender_id": b.tender_id,
            "vendor_id": b.vendor_id,
            "vendor_name": b.vendor.vendor_name if b.vendor else "Unknown",
            "bid_amount_inr": b.bid_amount_inr,
            "submission_timestamp": b.submission_timestamp.strftime("%Y-%m-%d %H:%M:%S") if b.submission_timestamp else None,
            "bid_status": b.bid_status,
            "disqualification_reason": b.disqualification_reason,
            "technical_score": b.technical_score,
            "financial_score": b.financial_score,
            "is_winner": b.is_winner
        })
    res.sort(key=lambda x: (x["bid_status"] == "DISQUALIFIED", x["bid_amount_inr"]))
    return res

@router.get("/{tender_id}/risk")
def get_tender_risk(tender_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    t = resolve_tender(tender_id, db)
    if not t:
        raise HTTPException(status_code=404, detail=f"Tender {tender_id} not found")

    inv = t.investigation
    signals_list = []
    if inv:
        for s in inv.signals:
            signals_list.append({
                "id": s.id,
                "indicator_code": s.indicator_code,
                "indicator_name": s.indicator_name,
                "title": s.title,
                "description": s.description,
                "severity": s.severity,
                "confidence": s.confidence,
                "signal_category": s.signal_category,
                "evidence": s.evidence_json
            })

    return {
        "tender_id": t.tender_id,
        "priority_score": inv.priority_score if inv else 12.0,
        "priority_tier": inv.priority_tier if inv else "Low",
        "signals_count": len(signals_list),
        "signals": signals_list,
        "responsible_ai_disclaimer": "ProcureShield AI identifies unusual procurement patterns, connects evidence, and prioritizes cases for human review. It does not determine guilt, corruption, or criminal conduct."
    }

@router.get("/{tender_id}/investigation")
def get_tender_investigation(tender_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    t = resolve_tender(tender_id, db)
    if not t:
        raise HTTPException(status_code=404, detail=f"Tender {tender_id} not found")

    award = t.award
    contract = t.contract
    inv = t.investigation

    # 1. Bids & Vendors
    participating_vendor_ids = [b.vendor_id for b in t.bids]
    vendors = db.query(Vendor).filter(Vendor.vendor_id.in_(participating_vendor_ids)).all()
    vendor_map = {v.vendor_id: v for v in vendors}

    bids_data = []
    for b in t.bids:
        v_obj = vendor_map.get(b.vendor_id)
        bids_data.append({
            "bid_id": b.bid_id,
            "vendor_id": b.vendor_id,
            "vendor_name": v_obj.vendor_name if v_obj else "Unknown",
            "bid_amount_inr": b.bid_amount_inr,
            "submission_timestamp": b.submission_timestamp.strftime("%Y-%m-%d %H:%M:%S") if b.submission_timestamp else None,
            "bid_status": b.bid_status,
            "disqualification_reason": b.disqualification_reason,
            "technical_score": b.technical_score,
            "financial_score": b.financial_score,
            "is_winner": b.is_winner,
            "variance_from_estimate_pct": round(((b.bid_amount_inr - t.estimated_value_inr) / t.estimated_value_inr) * 100, 2)
        })
    bids_data.sort(key=lambda x: (x["bid_status"] == "DISQUALIFIED", x["bid_amount_inr"]))

    # 2. Historical Vendor Statistics
    vendor_stats = []
    for v in vendors:
        v_awards = db.query(Award).filter(Award.winner_vendor_id == v.vendor_id).count()
        v_bids = db.query(Bid).filter(Bid.vendor_id == v.vendor_id).count()
        v_buyer_awards = db.query(Award).join(Tender).filter(Award.winner_vendor_id == v.vendor_id, Tender.buyer_id == t.buyer_id).count()
        vendor_stats.append({
            "vendor_id": v.vendor_id,
            "vendor_name": v.vendor_name,
            "director_id": v.director_id,
            "registered_address": v.registered_address,
            "total_bids": v_bids,
            "total_wins": v_awards,
            "win_rate_pct": round((v_awards / max(1, v_bids)) * 100, 1),
            "buyer_specific_wins": v_buyer_awards,
            "risk_level": v.risk_level
        })

    # 3. Together Participation among participating vendors
    together_data = []
    for i in range(len(participating_vendor_ids)):
        for j in range(i + 1, len(participating_vendor_ids)):
            v1, v2 = participating_vendor_ids[i], participating_vendor_ids[j]
            vtp = db.query(VendorTogetherParticipation).filter(
                or_(
                    (VendorTogetherParticipation.vendor_1 == v1) & (VendorTogetherParticipation.vendor_2 == v2),
                    (VendorTogetherParticipation.vendor_1 == v2) & (VendorTogetherParticipation.vendor_2 == v1)
                )
            ).first()
            if vtp and vtp.together_tender_count >= 2:
                together_data.append({
                    "vendor_1": v1,
                    "vendor_1_name": vendor_map.get(v1, {}).vendor_name if v1 in vendor_map else v1,
                    "vendor_2": v2,
                    "vendor_2_name": vendor_map.get(v2, {}).vendor_name if v2 in vendor_map else v2,
                    "together_tender_count": vtp.together_tender_count,
                    "together_percentage": vtp.together_percentage
                })
    together_data.sort(key=lambda x: x["together_tender_count"], reverse=True)

    # 4. Corporate Relationships among participating vendors
    relationships_data = []
    for i in range(len(participating_vendor_ids)):
        for j in range(i + 1, len(participating_vendor_ids)):
            v1, v2 = participating_vendor_ids[i], participating_vendor_ids[j]
            rels = db.query(VendorRelationship).filter(
                or_(
                    (VendorRelationship.vendor_1 == v1) & (VendorRelationship.vendor_2 == v2),
                    (VendorRelationship.vendor_1 == v2) & (VendorRelationship.vendor_2 == v1)
                )
            ).all()
            for r in rels:
                relationships_data.append({
                    "relationship_id": r.relationship_id,
                    "vendor_1": r.vendor_1,
                    "vendor_1_name": vendor_map.get(r.vendor_1, {}).vendor_name if r.vendor_1 in vendor_map else r.vendor_1,
                    "vendor_2": r.vendor_2,
                    "vendor_2_name": vendor_map.get(r.vendor_2, {}).vendor_name if r.vendor_2 in vendor_map else r.vendor_2,
                    "relationship_type": r.relationship_type,
                    "relationship_value": r.relationship_value,
                    "confidence": r.confidence
                })

    # 5. Detected Signals (C1–C20)
    signals_data = []
    if inv:
        for s in inv.signals:
            signals_data.append({
                "id": s.id,
                "indicator_code": s.indicator_code,
                "indicator_name": s.indicator_name,
                "title": s.title,
                "description": s.description,
                "severity": s.severity,
                "confidence": s.confidence,
                "signal_category": s.signal_category,
                "evidence": s.evidence_json
            })

    # 6. Investigation Notes
    notes_data = []
    if inv:
        for n in sorted(inv.notes, key=lambda x: x.created_at, reverse=True):
            notes_data.append({
                "id": n.id,
                "author_name": n.author_name,
                "note_text": n.note_text,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S") if n.created_at else None
            })

    return {
        "tender_id": t.tender_id,
        "case_code": inv.case_code if inv else f"CASE-{t.tender_id}",
        "tender_details": {
            "tender_id": t.tender_id,
            "title": t.tender_title,
            "category": t.category,
            "sub_category": t.sub_category,
            "buyer_id": t.buyer_id,
            "buyer_name": t.buyer_name,
            "location": t.location,
            "state": t.state,
            "estimated_value_inr": t.estimated_value_inr,
            "procurement_method": t.procurement_method,
            "award_criteria": t.award_criteria,
            "publication_date": t.publication_date.strftime("%Y-%m-%d %H:%M:%S") if t.publication_date else None,
            "submission_deadline": t.submission_deadline.strftime("%Y-%m-%d %H:%M:%S") if t.submission_deadline else None,
            "status": t.status
        },
        "winner": {
            "vendor_id": award.winner_vendor_id if award else None,
            "vendor_name": award.vendor.vendor_name if (award and award.vendor) else None,
            "awarded_amount_inr": award.awarded_amount_inr if award else None,
            "award_date": award.award_date.strftime("%Y-%m-%d") if (award and award.award_date) else None,
            "variance_pct": round(((award.awarded_amount_inr - t.estimated_value_inr) / t.estimated_value_inr) * 100, 2) if award else 0.0
        } if award else None,
        "contract": {
            "contract_id": contract.contract_id,
            "contract_value_inr": contract.contract_value_inr,
            "start_date": contract.start_date.strftime("%Y-%m-%d") if contract.start_date else None,
            "planned_end_date": contract.planned_end_date.strftime("%Y-%m-%d") if contract.planned_end_date else None,
            "actual_end_date": contract.actual_end_date.strftime("%Y-%m-%d") if contract.actual_end_date else None,
            "planned_duration_days": contract.planned_duration_days,
            "actual_duration_days": contract.actual_duration_days,
            "completion_status": contract.completion_status
        } if contract else None,
        "bids": bids_data,
        "vendor_history": vendor_stats,
        "together_participation": together_data,
        "vendor_relationships": relationships_data,
        "risk_signals": signals_data,
        "signals_count": len(signals_data),
        "priority_score": inv.priority_score if inv else 12.0,
        "priority_tier": inv.priority_tier if inv else "Low",
        "investigation_status": inv.status if inv else "NEW",
        "assigned_investigator": inv.assigned_investigator if inv else None,
        "summary_narrative": inv.summary_narrative if inv else None,
        "notes": notes_data,
        "responsible_ai_disclaimer": "ProcureShield AI identifies unusual procurement patterns, connects evidence, and prioritizes cases for human review. It does not determine guilt, corruption, or criminal conduct."
    }
