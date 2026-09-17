from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

# Auth & User
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "CITIZEN"
    department: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Reviewer
class ReviewerProfileResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    reputation_score: float
    total_reports: int
    verified_reports: int
    false_reports: int
    rank: int
    badges: List[str]

# Vendor & Network Graph
class VendorResponse(BaseModel):
    id: int
    name: str
    registration_number: str
    category: str
    win_rate: float
    total_contracts: int
    total_contract_value: float
    avg_delay_days: float
    quality_score: float
    complaint_rate: float
    maintenance_cost_ratio: float
    risk_level: str
    city: Optional[str] = None
    state: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # VENDOR, DIRECTOR, ADDRESS, PROJECT
    risk: Optional[str] = "LOW"
    meta: Optional[Dict[str, Any]] = None

class GraphEdge(BaseModel):
    source: str
    target: str
    label: str
    type: str # SHARED_DIRECTOR, SHARED_ADDRESS, CO_BIDDING, SUBCONTRACT
    weight: Optional[float] = 1.0

class VendorNetworkResponse(BaseModel):
    vendor_id: int
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# Tenders & Bids
class BidResponse(BaseModel):
    id: int
    tender_id: int
    vendor_id: int
    vendor_name: str
    bid_amount: float
    submission_time: datetime
    rank: int
    is_winning: bool
    technical_score: float
    pricing_deviation_pct: float

class TenderResponse(BaseModel):
    id: int
    tender_code: str
    title: str
    description: Optional[str] = None
    department: str
    category: str
    estimated_value: float
    publication_date: datetime
    submission_deadline: datetime
    status: str
    winning_vendor_id: Optional[int] = None
    winning_vendor_name: Optional[str] = None
    winning_bid_amount: Optional[float] = None
    location: Optional[str] = None
    bids: Optional[List[BidResponse]] = []
    model_config = ConfigDict(from_attributes=True)

# Project & Execution
class ProjectResponse(BaseModel):
    id: int
    contract_id: int
    name: str
    description: Optional[str] = None
    category: str
    department: str
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    planned_duration_days: int
    actual_duration_days: int
    delay_days: int
    planned_cost: float
    actual_cost: float
    cost_overrun_pct: float
    execution_status: str
    quality_status: str
    vendor_id: Optional[int] = None
    vendor_name: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Complaints & Media
class ComplaintCreate(BaseModel):
    project_id: Optional[int] = None
    tender_id: Optional[str] = None
    title: str
    description: str
    category: str
    rating: int = 3
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    media_url: Optional[str] = None

class ComplaintMediaResponse(BaseModel):
    id: int
    media_url: str
    media_type: str
    description: Optional[str] = None

class ComplaintResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    tender_id: Optional[str] = None
    project_name: Optional[str] = None
    citizen_id: int
    citizen_name: str
    title: str
    description: str
    category: str
    rating: int
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    reviewer_credibility_weight: float
    created_at: datetime
    media: List[ComplaintMediaResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ComplaintVerificationRequest(BaseModel):
    status: str  # VERIFIED or UNVERIFIED

# Investigation Notes
class InvestigationNoteCreate(BaseModel):
    note_text: str

class InvestigationNoteResponse(BaseModel):
    id: int
    author_name: str
    note_text: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Risk Signals & Alerts
class RiskSignalResponse(BaseModel):
    id: int
    signal_category: str
    title: str
    description: str
    severity: str
    confidence: float
    peer_benchmark_info: Optional[str] = None
    supporting_evidence_json: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    case_code: str
    tender_id: int
    vendor_id: int
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    vendor_name: Optional[str] = None
    priority_score: float
    priority_tier: str
    status: str
    assigned_investigator_name: Optional[str] = None
    main_signal: str
    procurement_risk: float
    network_risk: float
    price_risk: float
    execution_risk: float
    quality_risk: float
    feedback_risk: float
    maintenance_risk: float
    confidence_score: float
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    signals_count: Optional[int] = 0
    model_config = ConfigDict(from_attributes=True)

class AlertDetailResponse(AlertResponse):
    signals: List[RiskSignalResponse] = []
    notes: List[InvestigationNoteResponse] = []
    project_detail: Optional[ProjectResponse] = None
    vendor_detail: Optional[VendorResponse] = None
    tender_detail: Optional[TenderResponse] = None
    complaints: Optional[List[ComplaintResponse]] = []

class StatusUpdateRequest(BaseModel):
    status: str  # NEW, UNDER_REVIEW, EVIDENCE_GATHERING, ESCALATED, RESOLVED, DISMISSED, MONITORING
    assigned_investigator_id: Optional[int] = None
    note: Optional[str] = None

# AI Assistant
class AIAssistantQuery(BaseModel):
    alert_id: int
    question: str

class AIAssistantResponse(BaseModel):
    answer: str
    cited_evidence: List[Dict[str, Any]]
    confidence: float

class AICaseSummaryResponse(BaseModel):
    alert_id: int
    case_code: str
    priority_score: float
    observed_evidence: List[str]
    ai_signals: List[str]
    investigator_actions: List[str]
    full_narrative: str

# Audit Log
class AuditLogResponse(BaseModel):
    id: int
    user_email: Optional[str] = None
    action: str
    case_code: Optional[str] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
