from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import require_investigator
from backend.app.models.entities import Alert, InvestigationNote, AuditLog, User
from backend.app.schemas.schemas import StatusUpdateRequest, InvestigationNoteCreate, InvestigationNoteResponse

router = APIRouter(prefix="/investigations", tags=["Case Management & Audit"])

@router.post("/{alert_id}/status")
def update_case_status(
    alert_id: int,
    req: StatusUpdateRequest,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Case not found")
        
    prev_status = alert.status
    alert.status = req.status.upper()
    if not alert.assigned_investigator:
        alert.assigned_investigator = current_user.name
        
    alert.updated_at = datetime.utcnow()
    
    if req.note:
        note = InvestigationNote(
            investigation_id=alert.id,
            author_name=current_user.name,
            note_text=f"[Status changed to {alert.status}] {req.note}"
        )
        db.add(note)
        
    # Create Audit Log record (PRD Section 55)
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action=f"Status updated from '{prev_status}' to '{alert.status}'",
        case_code=alert.case_code,
        previous_state=prev_status,
        new_state=alert.status,
        ip_address="127.0.0.1"
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)
    
    return {
        "status": "success",
        "case_code": alert.case_code,
        "previous_status": prev_status,
        "new_status": alert.status,
        "assigned_investigator": alert.assigned_investigator if isinstance(alert.assigned_investigator, str) else (alert.assigned_investigator.name if alert.assigned_investigator else None)
    }

@router.post("/{alert_id}/notes", response_model=InvestigationNoteResponse)
def add_case_note(
    alert_id: int,
    req: InvestigationNoteCreate,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Case not found")
        
    note = InvestigationNote(
        investigation_id=alert.id,
        author_name=current_user.name,
        note_text=req.note_text
    )
    db.add(note)
    
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="Added investigation note",
        case_code=alert.case_code,
        previous_state=alert.status,
        new_state=alert.status,
        ip_address="127.0.0.1"
    )
    db.add(audit)
    db.commit()
    db.refresh(note)
    
    return InvestigationNoteResponse(
        id=note.id,
        author_name=current_user.name,
        note_text=note.note_text,
        created_at=note.created_at
    )
