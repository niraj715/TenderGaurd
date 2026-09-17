from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import Project, Contract, Vendor
from backend.app.schemas.schemas import ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
def get_projects(
    category: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Project)
    if category:
        query = query.filter(Project.category == category)
    if department:
        query = query.filter(Project.department == department)
    if status:
        query = query.filter(Project.execution_status == status.upper())
    if search:
        query = query.filter(Project.name.ilike(f"%{search}%") | Project.location_name.ilike(f"%{search}%"))
        
    projects = query.order_by(Project.created_at.desc()).all()
    results = []
    for p in projects:
        c = p.contract
        v_id = c.vendor.id if (c and c.vendor) else (int(c.vendor_id.replace("V", "")) if c and c.vendor_id and c.vendor_id.startswith("V") else None)
        v_name = c.vendor.vendor_name if (c and c.vendor) else "Contractor"
        results.append(ProjectResponse(
            id=p.id,
            contract_id=p.contract_id,
            name=p.name,
            description=p.description,
            category=p.category,
            department=p.department,
            location_name=p.location_name,
            latitude=p.latitude,
            longitude=p.longitude,
            planned_duration_days=p.planned_duration_days,
            actual_duration_days=p.actual_duration_days,
            delay_days=p.delay_days,
            planned_cost=p.planned_cost,
            actual_cost=p.actual_cost,
            cost_overrun_pct=p.cost_overrun_pct,
            execution_status=p.execution_status,
            quality_status=p.quality_status,
            vendor_id=v_id,
            vendor_name=v_name,
            created_at=p.created_at
        ))
    return results

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
        
    c = p.contract
    v_id = c.vendor.id if (c and c.vendor) else (int(c.vendor_id.replace("V", "")) if c and c.vendor_id and c.vendor_id.startswith("V") else None)
    v_name = c.vendor.vendor_name if (c and c.vendor) else "Contractor"
    return ProjectResponse(
        id=p.id,
        contract_id=p.contract_id,
        name=p.name,
        description=p.description,
        category=p.category,
        department=p.department,
        location_name=p.location_name,
        latitude=p.latitude,
        longitude=p.longitude,
        planned_duration_days=p.planned_duration_days,
        actual_duration_days=p.actual_duration_days,
        delay_days=p.delay_days,
        planned_cost=p.planned_cost,
        actual_cost=p.actual_cost,
        cost_overrun_pct=p.cost_overrun_pct,
        execution_status=p.execution_status,
        quality_status=p.quality_status,
        vendor_id=vendor_id,
        vendor_name=vendor_name,
        created_at=p.created_at
    )
