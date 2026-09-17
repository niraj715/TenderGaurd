from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.entities import ReviewerProfile, User
from backend.app.schemas.schemas import ReviewerProfileResponse

router = APIRouter(prefix="/reviewers", tags=["Reviewer Leaderboard & Reputation"])

@router.get("/leaderboard", response_model=List[ReviewerProfileResponse])
def get_leaderboard(timeframe: Optional[str] = "all_time", db: Session = Depends(get_db)):
    profiles = db.query(ReviewerProfile).order_by(ReviewerProfile.reputation_score.desc()).limit(20).all()
    results = []
    for idx, p in enumerate(profiles, start=1):
        badges_list = [b.strip() for b in p.badges.split(",")] if p.badges else ["Community Watcher"]
        results.append(ReviewerProfileResponse(
            id=p.id,
            user_id=p.user_id,
            user_name=p.user.name if p.user else f"Citizen #{p.user_id}",
            reputation_score=round(p.reputation_score, 1),
            total_reports=p.total_reports,
            verified_reports=p.verified_reports,
            false_reports=p.false_reports,
            rank=idx,
            badges=badges_list
        ))
    return results

@router.get("/me", response_model=ReviewerProfileResponse)
def get_my_reviewer_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(ReviewerProfile).filter(ReviewerProfile.user_id == current_user.id).first()
    if not p:
        # Create one if not exists
        p = ReviewerProfile(
            user_id=current_user.id,
            reputation_score=75.0,
            total_reports=0,
            verified_reports=0,
            false_reports=0,
            badges="Community Watcher",
            rank=10
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        
    badges_list = [b.strip() for b in p.badges.split(",")] if p.badges else ["Community Watcher"]
    return ReviewerProfileResponse(
        id=p.id,
        user_id=p.user_id,
        user_name=current_user.name,
        reputation_score=round(p.reputation_score, 1),
        total_reports=p.total_reports,
        verified_reports=p.verified_reports,
        false_reports=p.false_reports,
        rank=p.rank,
        badges=badges_list
    )
