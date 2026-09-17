from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

# -------------------------------------------------------------
# 1. CORE AUTH & REVIEWER PROFILES
# -------------------------------------------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="INVESTIGATOR")  # CITIZEN, INVESTIGATOR, OFFICIAL, RESEARCHER
    department = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaints = relationship("Complaint", back_populates="citizen")
    reviewer_profile = relationship("ReviewerProfile", back_populates="user", uselist=False)

class ReviewerProfile(Base):
    __tablename__ = "reviewer_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    reputation_score = Column(Float, default=70.0)  # 0 to 100
    total_reports = Column(Integer, default=0)
    verified_reports = Column(Integer, default=0)
    false_reports = Column(Integer, default=0)
    rank = Column(Integer, default=1)
    badges = Column(Text, default="Community Watcher")

    user = relationship("User", back_populates="reviewer_profile")
    contributions = relationship("ReviewerContribution", back_populates="reviewer")

class ReviewerContribution(Base):
    __tablename__ = "reviewer_contributions"
    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("reviewer_profiles.id", ondelete="CASCADE"))
    complaint_id = Column(Integer, nullable=True)
    points_earned = Column(Integer, default=10)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviewer = relationship("ReviewerProfile", back_populates="contributions")

# -------------------------------------------------------------
# 2. VENDORS & CORPORATE RELATIONSHIPS
# -------------------------------------------------------------
class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. V001
    vendor_name = Column(String(255), index=True, nullable=False)
    registration_number = Column(String(100), unique=True, index=True, nullable=False)
    director_id = Column(String(100), index=True, nullable=True)
    registered_address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    company_type = Column(String(100), default="Private Limited")
    registration_date = Column(DateTime, nullable=True)
    industry_category = Column(String(100), default="Civil Infrastructure")
    
    win_rate = Column(Float, default=0.0)
    total_contracts = Column(Integer, default=0)
    total_contract_value = Column(Float, default=0.0)
    avg_delay_days = Column(Float, default=0.0)
    risk_level = Column(String(50), default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow)

    # Legacy alias properties for backward compatibility
    @property
    def name(self):
        return self.vendor_name

    @property
    def category(self):
        return self.industry_category

    bids = relationship("Bid", back_populates="vendor", foreign_keys="Bid.vendor_id")
    awards = relationship("Award", back_populates="vendor", foreign_keys="Award.winner_vendor_id")
    contracts = relationship("Contract", back_populates="vendor", foreign_keys="Contract.vendor_id")

class VendorRelationship(Base):
    __tablename__ = "vendor_relationships"
    id = Column(Integer, primary_key=True, index=True)
    relationship_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. R01
    vendor_1 = Column(String(50), ForeignKey("vendors.vendor_id"), nullable=False)
    vendor_2 = Column(String(50), ForeignKey("vendors.vendor_id"), nullable=False)
    relationship_type = Column(String(100), nullable=False) # shared_director, shared_address, shared_phone, shared_email, common_parent
    relationship_value = Column(String(255), nullable=False)
    confidence = Column(Float, default=0.95)
    created_at = Column(DateTime, default=datetime.utcnow)

    v1 = relationship("Vendor", foreign_keys=[vendor_1])
    v2 = relationship("Vendor", foreign_keys=[vendor_2])

class VendorTogetherParticipation(Base):
    __tablename__ = "vendor_together_participation"
    id = Column(Integer, primary_key=True, index=True)
    vendor_1 = Column(String(50), ForeignKey("vendors.vendor_id"), nullable=False, index=True)
    vendor_2 = Column(String(50), ForeignKey("vendors.vendor_id"), nullable=False, index=True)
    together_tender_count = Column(Integer, nullable=False, default=1)
    together_percentage = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    v1 = relationship("Vendor", foreign_keys=[vendor_1])
    v2 = relationship("Vendor", foreign_keys=[vendor_2])

# -------------------------------------------------------------
# 3. TENDERS, BIDS, AWARDS, CONTRACTS
# -------------------------------------------------------------
class Tender(Base):
    __tablename__ = "tenders"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. T001
    buyer_id = Column(String(50), index=True, nullable=False)
    buyer_name = Column(String(255), nullable=False)
    tender_title = Column(Text, nullable=False)
    category = Column(String(100), index=True, nullable=False)
    sub_category = Column(String(150), nullable=True)
    location = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    estimated_value_inr = Column(Float, nullable=False)
    procurement_method = Column(String(100), default="Open Competitive Bidding")
    award_criteria = Column(String(100), default="Lowest Evaluated Responsive Bid (L1)")
    publication_date = Column(DateTime, nullable=False)
    submission_deadline = Column(DateTime, nullable=False)
    technical_evaluation_date = Column(DateTime, nullable=True)
    financial_evaluation_date = Column(DateTime, nullable=True)
    award_date = Column(DateTime, nullable=True)
    contract_duration_days = Column(Integer, default=180)
    status = Column(String(50), default="AWARDED") # AWARDED, EVALUATION, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Legacy alias properties
    @property
    def tender_code(self):
        return self.tender_id

    @property
    def title(self):
        return self.tender_title

    @property
    def department(self):
        return self.buyer_name

    @property
    def title(self):
        return self.tender_title

    @property
    def estimated_value(self):
        return self.estimated_value_inr

    @property
    def winning_bid_amount(self):
        if self.award:
            return self.award.awarded_amount_inr
        return self.estimated_value_inr

    bids = relationship("Bid", back_populates="tender", cascade="all, delete-orphan", foreign_keys="Bid.tender_id")
    award = relationship("Award", back_populates="tender", uselist=False, foreign_keys="Award.tender_id")
    contract = relationship("Contract", back_populates="tender", uselist=False, foreign_keys="Contract.tender_id")
    projects = relationship("Project", back_populates="tender", foreign_keys="Project.tender_id")
    investigation = relationship("Investigation", back_populates="tender", uselist=False, foreign_keys="Investigation.tender_id")
    risk_signals = relationship("RiskSignal", back_populates="tender", cascade="all, delete-orphan", foreign_keys="RiskSignal.tender_id")

class Bid(Base):
    __tablename__ = "bids"
    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. B0001
    tender_id = Column(String(50), ForeignKey("tenders.tender_id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id = Column(String(50), ForeignKey("vendors.vendor_id", ondelete="CASCADE"), nullable=False, index=True)
    bid_amount_inr = Column(Float, nullable=False)
    submission_timestamp = Column(DateTime, nullable=False)
    bid_status = Column(String(50), default="QUALIFIED") # QUALIFIED, DISQUALIFIED
    disqualification_reason = Column(Text, nullable=True)
    technical_score = Column(Float, default=85.0)
    financial_score = Column(Float, default=85.0)
    is_winner = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Legacy alias properties
    @property
    def bid_amount(self):
        return self.bid_amount_inr

    @property
    def is_winning(self):
        return self.is_winner

    tender = relationship("Tender", back_populates="bids", foreign_keys=[tender_id])
    vendor = relationship("Vendor", back_populates="bids", foreign_keys=[vendor_id])

class Award(Base):
    __tablename__ = "awards"
    id = Column(Integer, primary_key=True, index=True)
    award_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. A001
    tender_id = Column(String(50), ForeignKey("tenders.tender_id", ondelete="CASCADE"), unique=True, nullable=False)
    winner_vendor_id = Column(String(50), ForeignKey("vendors.vendor_id", ondelete="CASCADE"), nullable=False)
    awarded_amount_inr = Column(Float, nullable=False)
    award_date = Column(DateTime, nullable=False)
    award_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tender = relationship("Tender", back_populates="award", foreign_keys=[tender_id])
    vendor = relationship("Vendor", back_populates="awards", foreign_keys=[winner_vendor_id])

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. C001
    tender_id = Column(String(50), ForeignKey("tenders.tender_id", ondelete="CASCADE"), unique=True, nullable=False)
    vendor_id = Column(String(50), ForeignKey("vendors.vendor_id", ondelete="CASCADE"), nullable=False)
    contract_value_inr = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    planned_end_date = Column(DateTime, nullable=False)
    actual_end_date = Column(DateTime, nullable=True)
    planned_duration_days = Column(Integer, nullable=False)
    actual_duration_days = Column(Integer, nullable=False)
    completion_status = Column(String(50), default="COMPLETED") # COMPLETED, DELAYED, IN_PROGRESS, TERMINATED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Legacy alias properties
    @property
    def contracted_amount(self):
        return self.contract_value_inr

    tender = relationship("Tender", back_populates="contract", foreign_keys=[tender_id])
    vendor = relationship("Vendor", back_populates="contracts", foreign_keys=[vendor_id])

# -------------------------------------------------------------
# 4. INVESTIGATIONS & ANOMALY RISK SIGNALS
# -------------------------------------------------------------
class Investigation(Base):
    __tablename__ = "investigations"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(50), ForeignKey("tenders.tender_id", ondelete="CASCADE"), unique=True, nullable=False)
    case_code = Column(String(100), unique=True, index=True, nullable=False) # e.g. CASE-T001
    priority_score = Column(Float, nullable=False) # 0 to 100
    priority_tier = Column(String(50), index=True, nullable=False) # Low, Moderate, Elevated, High, Critical
    status = Column(String(50), default="NEW", index=True) # NEW, UNDER_REVIEW, EVIDENCE_GATHERING, ESCALATED, RESOLVED, DISMISSED
    signals_count = Column(Integer, default=0)
    assigned_investigator = Column(String(150), nullable=True)
    summary_narrative = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tender = relationship("Tender", back_populates="investigation", foreign_keys=[tender_id])
    signals = relationship("RiskSignal", back_populates="investigation", cascade="all, delete-orphan")
    notes = relationship("InvestigationNote", back_populates="investigation", cascade="all, delete-orphan")

    @property
    def project(self):
        if self.tender and self.tender.projects:
            return self.tender.projects[0]
        return None

    @property
    def vendor(self):
        if self.tender and self.tender.award and self.tender.award.vendor:
            return self.tender.award.vendor
        return None

    @property
    def confidence_score(self):
        return 92.0

# Alias Alert to Investigation for existing code compatibility
Alert = Investigation

class RiskSignal(Base):
    __tablename__ = "risk_signals"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(50), ForeignKey("tenders.tender_id", ondelete="CASCADE"), nullable=False, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=True)
    indicator_code = Column(String(20), nullable=False, index=True) # C1 to C20
    indicator_name = Column(String(150), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Float, nullable=False) # 0.0 to 1.0
    confidence = Column(Float, nullable=False) # 0.0 to 1.0
    evidence_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Compatibility properties for PRD
    @property
    def signal_category(self):
        # Maps C1-C6 to Competition, C7-C10 to Pricing, C11-C13 to Vendor, C14-C16 to Pattern, C17 to Relationship, C18-C20 to Procedure
        code_num = int(self.indicator_code.replace("C", "")) if self.indicator_code.startswith("C") and self.indicator_code[1:].isdigit() else 1
        if code_num <= 6: return "COMPETITION"
        if code_num <= 10: return "PRICING"
        if code_num <= 13: return "VENDOR"
        if code_num <= 16: return "PATTERNS"
        if code_num == 17: return "RELATIONSHIPS"
        return "PROCEDURE"

    tender = relationship("Tender", back_populates="risk_signals", foreign_keys=[tender_id])
    investigation = relationship("Investigation", back_populates="signals", foreign_keys=[investigation_id])

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    author_name = Column(String(150), nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="notes")

class BenchmarkCase(Base):
    __tablename__ = "benchmark_cases"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(50), ForeignKey("tenders.tender_id", ondelete="CASCADE"), unique=True, nullable=False)
    expected_indicator_codes = Column(String(255), nullable=True)
    scenario_type = Column(String(255), nullable=True)
    benchmark_alert = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tender = relationship("Tender")

# -------------------------------------------------------------
# 5. OPTIONAL FIELD CITIZEN COMPLAINTS & AUDIT LOGS
# -------------------------------------------------------------
class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(50), ForeignKey("tenders.tender_id", ondelete="CASCADE"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    rating = Column(Integer, default=3)
    location = Column(String(255), nullable=True)
    latitude = Column(Float, default=30.9045)
    longitude = Column(Float, default=77.0967)
    status = Column(String(50), default="VERIFIED")
    reviewer_credibility_weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    citizen = relationship("User", back_populates="complaints")
    project = relationship("Project")
    media = relationship("ComplaintMedia", back_populates="complaint", cascade="all, delete-orphan")

class ComplaintMedia(Base):
    __tablename__ = "complaint_media"
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False)
    media_url = Column(String(255), nullable=False)
    media_type = Column(String(50), default="IMAGE")
    description = Column(String(255), nullable=True)

    complaint = relationship("Complaint", back_populates="media")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, nullable=True)
    tender_id = Column(String(50), ForeignKey("tenders.tender_id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="Civil Infrastructure")
    department = Column(String(150), default="PWD")
    location_name = Column(String(200), default="Solan")
    planned_duration_days = Column(Integer, default=180)
    actual_duration_days = Column(Integer, default=180)
    planned_cost = Column(Float, default=1000000.0)
    actual_cost = Column(Float, default=1000000.0)
    execution_status = Column(String(50), default="COMPLETED")
    quality_status = Column(String(50), default="SATISFACTORY")
    latitude = Column(Float, default=30.9045)
    longitude = Column(Float, default=77.0967)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def delay_days(self):
        return max(0, (self.actual_duration_days or 0) - (self.planned_duration_days or 0))

    @property
    def cost_overrun_pct(self):
        if self.planned_cost and self.planned_cost > 0:
            return max(0.0, round(((self.actual_cost or self.planned_cost) - self.planned_cost) / self.planned_cost * 100, 1))
        return 0.0

    @property
    def contract(self):
        if self.tender and self.tender.contract:
            return self.tender.contract
        return None

    tender = relationship("Tender", foreign_keys=[tender_id])
    inspections = relationship("Inspection", back_populates="project")
    quality_records = relationship("QualityRecord", back_populates="project")
    maintenance_records = relationship("MaintenanceRecord", back_populates="project")

class Inspection(Base):
    __tablename__ = "inspections"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    inspection_date = Column(DateTime, default=datetime.utcnow)
    inspector_name = Column(String(150), default="Site Inspector")
    inspector_agency = Column(String(150), default="Quality Assurance Cell")
    result = Column(String(50), default="PASS")
    specification_deviations = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    project = relationship("Project", back_populates="inspections")

class QualityRecord(Base):
    __tablename__ = "quality_records"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    defect_category = Column(String(100), default="Materials")
    severity = Column(String(50), default="MEDIUM")
    description = Column(Text, default="No defects observed")
    detected_date = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)

    project = relationship("Project", back_populates="quality_records")

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    maintenance_date = Column(DateTime, default=datetime.utcnow)
    cost = Column(Float, default=50000.0)
    vendor_id = Column(String(50), nullable=True)
    maintenance_type = Column(String(100), default="ROUTINE")
    benchmark_cost_ratio = Column(Float, default=1.0)
    description = Column(Text, nullable=True)

    project = relationship("Project", back_populates="maintenance_records")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(150), nullable=True)
    action = Column(String(150), nullable=False)
    case_code = Column(String(100), nullable=True)
    previous_state = Column(String(100), nullable=True)
    new_state = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
