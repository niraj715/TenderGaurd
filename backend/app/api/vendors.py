from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.database import get_db
from backend.app.core.security import require_investigator
from backend.app.models.entities import Vendor, VendorRelationship, Award, Bid, Contract, Tender, User

router = APIRouter(prefix="/vendors", tags=["Vendors & Corporate Networks"])

def resolve_vendor(vendor_id_or_code: str, db: Session) -> Optional[Vendor]:
    v = db.query(Vendor).filter(Vendor.vendor_id == str(vendor_id_or_code)).first()
    if v:
        return v
    if str(vendor_id_or_code).isdigit():
        v = db.query(Vendor).filter(Vendor.id == int(vendor_id_or_code)).first()
        if v:
            return v
        v = db.query(Vendor).filter(Vendor.vendor_id == f"V{int(vendor_id_or_code):03d}").first()
        if v:
            return v
    return None

@router.get("")
def get_vendors(
    category: Optional[str] = None,
    risk: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    query = db.query(Vendor)
    if category and category.lower() != "all":
        query = query.filter(Vendor.industry_category.ilike(f"%{category}%"))
    if risk and risk.lower() != "all":
        query = query.filter(Vendor.risk_level.ilike(risk))
    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            Vendor.vendor_name.ilike(s),
            Vendor.vendor_id.ilike(s),
            Vendor.city.ilike(s),
            Vendor.state.ilike(s)
        ))

    vendors = query.order_by(Vendor.total_contract_value.desc()).all()
    results = []
    for v in vendors:
        results.append({
            "id": v.id,
            "vendor_id": v.vendor_id,
            "vendor_code": v.vendor_id,
            "name": v.vendor_name,
            "vendor_name": v.vendor_name,
            "registration_number": v.registration_number,
            "director_id": v.director_id,
            "registered_address": v.registered_address,
            "city": v.city,
            "state": v.state,
            "phone": v.phone,
            "email": v.email,
            "company_type": v.company_type,
            "industry_category": v.industry_category,
            "category": v.industry_category,
            "win_rate": v.win_rate,
            "total_contracts": v.total_contracts,
            "total_contract_value": v.total_contract_value,
            "avg_delay_days": v.avg_delay_days,
            "risk_level": v.risk_level
        })
    return results

@router.get("/{vendor_id}")
def get_vendor(
    vendor_id: str,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    v = resolve_vendor(vendor_id, db)
    if not v:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found")

    awards = db.query(Award).join(Tender).filter(Award.winner_vendor_id == v.vendor_id).all()
    contracts = db.query(Contract).filter(Contract.vendor_id == v.vendor_id).all()
    bids = db.query(Bid).join(Tender).filter(Bid.vendor_id == v.vendor_id).all()

    recent_awards = []
    for a in awards[:10]:
        t = a.tender
        recent_awards.append({
            "tender_id": a.tender_id,
            "title": t.tender_title if t else "N/A",
            "category": t.category if t else "N/A",
            "buyer_name": t.buyer_name if t else "N/A",
            "awarded_amount_inr": a.awarded_amount_inr,
            "award_date": a.award_date.strftime("%Y-%m-%d") if a.award_date else None
        })

    return {
        "id": v.id,
        "vendor_id": v.vendor_id,
        "vendor_code": v.vendor_id,
        "name": v.vendor_name,
        "vendor_name": v.vendor_name,
        "registration_number": v.registration_number,
        "director_id": v.director_id,
        "registered_address": v.registered_address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "email": v.email,
        "company_type": v.company_type,
        "industry_category": v.industry_category,
        "category": v.industry_category,
        "win_rate": v.win_rate,
        "total_bids": len(bids),
        "total_contracts": v.total_contracts,
        "total_contract_value": v.total_contract_value,
        "avg_delay_days": v.avg_delay_days,
        "risk_level": v.risk_level,
        "recent_awards": recent_awards
    }

@router.get("/{vendor_id}/network")
def get_vendor_network(
    vendor_id: str,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    v = resolve_vendor(vendor_id, db)
    if not v:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found")

    v_code = v.vendor_id
    rels = db.query(VendorRelationship).filter(
        or_(VendorRelationship.vendor_1 == v_code, VendorRelationship.vendor_2 == v_code)
    ).all()

    nodes = []
    edges = []
    seen_nodes = set()

    # Center root vendor node
    root_id = f"vendor_{v_code}"
    nodes.append({
        "id": root_id,
        "label": v.vendor_name,
        "type": "PRIMARY_VENDOR",
        "risk": v.risk_level,
        "meta": {"code": v_code, "win_rate": v.win_rate, "contracts": v.total_contracts}
    })
    seen_nodes.add(root_id)

    for r in rels:
        other_code = r.vendor_2 if r.vendor_1 == v_code else r.vendor_1
        other_v = db.query(Vendor).filter(Vendor.vendor_id == other_code).first()
        other_name = other_v.vendor_name if other_v else other_code

        other_node_id = f"vendor_{other_code}"
        if other_node_id not in seen_nodes:
            nodes.append({
                "id": other_node_id,
                "label": other_name,
                "type": "RELATED_VENDOR",
                "risk": other_v.risk_level if other_v else "MEDIUM",
                "meta": {"code": other_code, "win_rate": other_v.win_rate if other_v else 0.0}
            })
            seen_nodes.add(other_node_id)

        # Shared attribute node (e.g. Director, Address, Phone, Email, Parent)
        entity_node_id = f"attr_{r.relationship_type}_{abs(hash(r.relationship_value)) % 100000}"
        if entity_node_id not in seen_nodes:
            attr_type = "DIRECTOR" if "director" in r.relationship_type.lower() else (
                "ADDRESS" if "address" in r.relationship_type.lower() else (
                    "CONTACT" if "phone" in r.relationship_type.lower() or "email" in r.relationship_type.lower() else "SUBSIDIARY"
                )
            )
            nodes.append({
                "id": entity_node_id,
                "label": r.relationship_value,
                "type": attr_type,
                "risk": "HIGH" if attr_type == "DIRECTOR" else "MEDIUM",
                "meta": {"relationship_type": r.relationship_type}
            })
            seen_nodes.add(entity_node_id)

        # Edges
        edges.append({
            "source": root_id,
            "target": entity_node_id,
            "label": r.relationship_type.replace("_", " ").title(),
            "type": r.relationship_type.upper(),
            "weight": r.confidence
        })
        edges.append({
            "source": entity_node_id,
            "target": other_node_id,
            "label": r.relationship_type.replace("_", " ").title(),
            "type": r.relationship_type.upper(),
            "weight": r.confidence
        })

    return {
        "vendor_id": v_code,
        "vendor_name": v.vendor_name,
        "nodes": nodes,
        "edges": edges
    }
