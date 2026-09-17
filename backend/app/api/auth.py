from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from backend.app.models.entities import User, ReviewerProfile, AuditLog
from backend.app.schemas.schemas import Token, LoginRequest, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    role_upper = user_in.role.upper()
    if role_upper not in ("INVESTIGATOR", "CITIZEN"):
        raise HTTPException(status_code=400, detail="Invalid role. System supports only 'INVESTIGATOR' and 'CITIZEN'.")

    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=role_upper,
        department=user_in.department,
        avatar_url=f"https://api.dicebear.com/7.x/bottts/svg?seed={user_in.name}"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create reviewer profile if citizen
    if user.role == "CITIZEN":
        rev = ReviewerProfile(
            user_id=user.id,
            reputation_score=70.0,
            total_reports=0,
            verified_reports=0,
            false_reports=0,
            badges="Community Watcher"
        )
        db.add(rev)
        db.commit()
        
    token = create_access_token({"sub": str(user.id), "role": user.role, "name": user.name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "department": user.department}
    }

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    token = create_access_token({"sub": str(user.id), "role": user.role, "name": user.name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "department": user.department}
    }

@router.post("/demo-login/{role}", response_model=Token)
def demo_login(role: str, db: Session = Depends(get_db)):
    role_upper = role.upper()
    if role_upper not in ("INVESTIGATOR", "CITIZEN"):
        raise HTTPException(status_code=400, detail="Invalid role. Demo login is available only for 'INVESTIGATOR' and 'CITIZEN'.")

    user = db.query(User).filter(User.role == role_upper).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"No user with role {role_upper} found in database")
            
    token = create_access_token({"sub": str(user.id), "role": user.role, "name": user.name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "department": user.department}
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
