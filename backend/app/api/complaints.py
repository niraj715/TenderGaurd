from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_investigator
from backend.app.models.entities import (
    Complaint, ComplaintMedia, Project, User, ReviewerProfile,
    ReviewerContribution, Alert, RiskSignal, Vendor, Tender
)
from backend.app.schemas.schemas import (
    ComplaintCreate, ComplaintResponse, ComplaintMediaResponse, ComplaintVerificationRequest
)

router = APIRouter(prefix="/complaints", tags=["Citizen Complaints"])

@router.get("", response_model=List[ComplaintResponse])
def get_complaints(
    project_id: Optional[int] = None,
    tender_id: Optional[str] = None,
    citizen_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    if project_id:
        query = query.filter(Complaint.project_id == project_id)
    if tender_id:
        query = query.filter(Complaint.tender_id == tender_id)
    if citizen_id:
        query = query.filter(Complaint.citizen_id == citizen_id)
    if status and status.lower() != "all":
        query = query.filter(Complaint.status == status.upper())
        
    complaints = query.order_by(Complaint.created_at.desc()).all()
    results = []
    for c in complaints:
        media_list = [
            ComplaintMediaResponse(
                id=m.id,
                media_url=m.media_url,
                media_type=m.media_type,
                description=m.description
            ) for m in c.media
        ]
        results.append(ComplaintResponse(
            id=c.id,
            project_id=c.project_id,
            tender_id=c.tender_id,
            project_name=c.project.name if c.project else (c.tender_id or "Public Project"),
            citizen_id=c.citizen_id,
            citizen_name=c.citizen.name if c.citizen else "Anonymous Citizen",
            title=c.title,
            description=c.description,
            category=c.category,
            rating=c.rating,
            location=c.location,
            latitude=c.latitude,
            longitude=c.longitude,
            status=c.status,
            reviewer_credibility_weight=c.reviewer_credibility_weight,
            created_at=c.created_at,
            media=media_list
        ))
    return results

@router.get("/my-reviews", response_model=List[ComplaintResponse])
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    complaints = db.query(Complaint).filter(Complaint.citizen_id == current_user.id).order_by(Complaint.created_at.desc()).all()
    results = []
    for c in complaints:
        media_list = [
            ComplaintMediaResponse(
                id=m.id,
                media_url=m.media_url,
                media_type=m.media_type,
                description=m.description
            ) for m in c.media
        ]
        results.append(ComplaintResponse(
            id=c.id,
            project_id=c.project_id,
            tender_id=c.tender_id,
            project_name=c.project.name if c.project else (c.tender_id or "Public Project"),
            citizen_id=c.citizen_id,
            citizen_name=current_user.name,
            title=c.title,
            description=c.description,
            category=c.category,
            rating=c.rating,
            location=c.location,
            latitude=c.latitude,
            longitude=c.longitude,
            status=c.status,
            reviewer_credibility_weight=c.reviewer_credibility_weight,
            created_at=c.created_at,
            media=media_list
        ))
    return results

@router.post("", response_model=ComplaintResponse)
def create_complaint(
    comp_in: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    proj = None
    tender = None
    if comp_in.tender_id:
        t_id_str = str(comp_in.tender_id).strip()
        tender = db.query(Tender).filter(Tender.tender_id == t_id_str).first()
        if not tender and t_id_str.isdigit():
            tender = db.query(Tender).filter(Tender.id == int(t_id_str)).first()
            if not tender:
                tender = db.query(Tender).filter(Tender.tender_id == f"T{int(t_id_str):03d}").first()
        if tender and tender.projects:
            proj = tender.projects[0]
        elif tender:
            proj = db.query(Project).filter(Project.tender_id == tender.tender_id).first()
            
    if comp_in.project_id and not proj:
        proj = db.query(Project).filter(Project.id == comp_in.project_id).first()
        if proj and proj.tender_id and not tender:
            tender = db.query(Tender).filter(Tender.tender_id == proj.tender_id).first()

    if not proj and not tender:
        raise HTTPException(status_code=404, detail="Valid Tender ID or Project ID must be provided")

    rev_profile = db.query(ReviewerProfile).filter(ReviewerProfile.user_id == current_user.id).first()
    if not rev_profile:
        rev_profile = ReviewerProfile(
            user_id=current_user.id,
            reputation_score=75.0,
            total_reports=0,
            verified_reports=0,
            false_reports=0,
            rank=15,
            badges="Community Watcher"
        )
        db.add(rev_profile)
        db.flush()

    credibility = (rev_profile.reputation_score / 100.0)

    t_code = tender.tender_id if tender else (proj.tender_id if proj else None)
    p_id = proj.id if proj else (tender.id if tender else None)
    p_name = proj.name if proj else (tender.tender_title if tender else "Public Project")
    loc = comp_in.location or (proj.location_name if proj else (tender.location if tender else "Solan"))
    lat = comp_in.latitude or (proj.latitude if proj else 30.9045) or 30.9045
    lon = comp_in.longitude or (proj.longitude if proj else 77.0967) or 77.0967

    complaint = Complaint(
        tender_id=t_code,
        project_id=p_id,
        citizen_id=current_user.id,
        title=comp_in.title,
        description=comp_in.description,
        category=comp_in.category,
        rating=comp_in.rating,
        location=loc,
        latitude=lat,
        longitude=lon,
        status="SUBMITTED",
        reviewer_credibility_weight=round(credibility, 2)
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    if comp_in.media_url:
        media = ComplaintMedia(
            complaint_id=complaint.id,
            media_url=comp_in.media_url,
            media_type="IMAGE",
            description="Citizen uploaded site photo"
        )
        db.add(media)
        db.commit()
        db.refresh(complaint)

    rev_profile.total_reports += 1
    rev_profile.reputation_score = min(100.0, rev_profile.reputation_score + 0.5)
    contrib = ReviewerContribution(
        reviewer_id=rev_profile.id,
        complaint_id=complaint.id,
        points_earned=10,
        description=f"Submitted field review for {p_name}"
    )
    db.add(contrib)
    db.commit()

    media_list = [
        ComplaintMediaResponse(
            id=m.id,
            media_url=m.media_url,
            media_type=m.media_type,
            description=m.description
        ) for m in complaint.media
    ]

    return ComplaintResponse(
        id=complaint.id,
        project_id=complaint.project_id,
        tender_id=complaint.tender_id,
        project_name=p_name,
        citizen_id=complaint.citizen_id,
        citizen_name=current_user.name,
        title=complaint.title,
        description=complaint.description,
        category=complaint.category,
        rating=complaint.rating,
        location=complaint.location,
        latitude=complaint.latitude,
        longitude=complaint.longitude,
        status=complaint.status,
        reviewer_credibility_weight=complaint.reviewer_credibility_weight,
        created_at=complaint.created_at,
        media=media_list
    )

@router.post("/{complaint_id}/verify", response_model=ComplaintResponse)
def verify_complaint(
    complaint_id: int,
    verif_in: ComplaintVerificationRequest,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    complaint.status = verif_in.status.upper()
    db.commit()
    
    # Update reviewer reputation
    rev_profile = db.query(ReviewerProfile).filter(ReviewerProfile.user_id == complaint.citizen_id).first()
    if rev_profile:
        if complaint.status == "VERIFIED":
            rev_profile.verified_reports += 1
            rev_profile.reputation_score = min(100.0, rev_profile.reputation_score + 2.5)
            contrib = ReviewerContribution(
                reviewer_id=rev_profile.id,
                complaint_id=complaint.id,
                points_earned=15,
                description=f"Report #{complaint.id} on '{complaint.project.name}' verified by investigator"
            )
            db.add(contrib)
        elif complaint.status == "UNVERIFIED":
            rev_profile.false_reports += 1
            rev_profile.reputation_score = max(30.0, rev_profile.reputation_score - 3.0)
        db.commit()
        
    # Recompute risk score for the project & alert if verified!
    project = complaint.project
    tender = project.tender if project and project.tender else (
        db.query(Tender).filter(Tender.tender_id == complaint.tender_id).first() if complaint.tender_id else None
    )
    if tender and tender.investigation and complaint.status == "VERIFIED":
        tender.investigation.signals_count = (tender.investigation.signals_count or 0) + 1
        tender.investigation.updated_at = datetime.utcnow()
        db.commit()

    media_list = [
        ComplaintMediaResponse(
            id=m.id,
            media_url=m.media_url,
            media_type=m.media_type,
            description=m.description
        ) for m in complaint.media
    ]
    return ComplaintResponse(
        id=complaint.id,
        project_id=complaint.project_id,
        project_name=complaint.project.name if complaint.project else None,
        citizen_id=complaint.citizen_id,
        citizen_name=complaint.citizen.name if complaint.citizen else "Citizen",
        title=complaint.title,
        description=complaint.description,
        category=complaint.category,
        rating=complaint.rating,
        location=complaint.location,
        latitude=complaint.latitude,
        longitude=complaint.longitude,
        status=complaint.status,
        reviewer_credibility_weight=complaint.reviewer_credibility_weight,
        created_at=complaint.created_at,
        media=media_list
    )
