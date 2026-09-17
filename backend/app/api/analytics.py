from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.database import get_db
from backend.app.core.security import require_investigator
from backend.app.models.entities import Tender, Vendor, Investigation, Project, Complaint, AuditLog, RiskSignal, User
from backend.app.schemas.schemas import AuditLogResponse

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard KPIs"])

@router.get("/overview")
@router.get("/kpis")
def get_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    tenders_count = db.query(Tender).count()
    vendors_count = db.query(Vendor).count()
    alerts_count = db.query(Investigation).filter(Investigation.priority_tier.in_(["Elevated", "High", "Critical"])).count()
    critical_count = db.query(Investigation).filter(Investigation.priority_tier == "Critical").count()
    high_count = db.query(Investigation).filter(Investigation.priority_tier == "High").count()
    moderate_count = db.query(Investigation).filter(Investigation.priority_tier.in_(["Moderate", "Elevated", "Medium"])).count()
    low_count = db.query(Investigation).filter(Investigation.priority_tier == "Low").count()
    citizen_reviews_count = db.query(Complaint).count()
    projects_count = db.query(Project).count()

    total_volume = db.query(func.sum(Tender.estimated_value_inr)).scalar() or 0.0
    avg_score = db.query(func.avg(Investigation.priority_score)).scalar() or 0.0

    return {
        "tenders_analyzed": tenders_count,
        "vendors_monitored": vendors_count,
        "active_alerts": alerts_count,
        "total_alerts": alerts_count,
        "critical_cases": critical_count,
        "citizen_reviews": citizen_reviews_count,
        "projects_monitored": projects_count,
        "total_procurement_volume": round(total_volume, 2),
        "average_investigation_priority": round(avg_score, 1),
        "tier_distribution": {
            "Critical": critical_count,
            "High": high_count,
            "Moderate": moderate_count,
            "Medium": moderate_count,
            "Low": low_count
        }
    }

@router.get("/risk-trends")
def get_risk_trends(
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    distinct_cats = db.query(Tender.category).distinct().all()
    categories = [c[0] for c in distinct_cats if c[0]]
    category_data = []
    for cat in categories:
        cnt = db.query(Investigation).join(Tender).filter(Tender.category == cat, Investigation.priority_tier.in_(["Elevated", "High", "Critical"])).count()
        avg_score = db.query(func.avg(Investigation.priority_score)).join(Tender).filter(Tender.category == cat).scalar() or 25.0
        category_data.append({"category": cat, "case_count": cnt, "avg_priority": round(avg_score, 1)})

    tiers = {
        "CRITICAL": db.query(Investigation).filter(Investigation.priority_tier == "Critical").count(),
        "HIGH": db.query(Investigation).filter(Investigation.priority_tier == "High").count(),
        "MEDIUM": db.query(Investigation).filter(Investigation.priority_tier.in_(["Moderate", "Elevated", "Medium"])).count(),
        "LOW": db.query(Investigation).filter(Investigation.priority_tier == "Low").count(),
    }

    return {
        "category_breakdown": category_data,
        "tier_distribution": tiers
    }

@router.get("/audit-trail", response_model=List[AuditLogResponse])
def get_audit_trail(
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(25).all()
    return logs
