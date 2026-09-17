import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.core.security import get_password_hash
from backend.app.models.entities import (
    User, ReviewerProfile, ReviewerContribution, Vendor, VendorRelationship,
    Tender, Bid, Contract, Project, Inspection, QualityRecord, Complaint,
    ComplaintMedia, MaintenanceRecord, Alert, RiskSignal, InvestigationNote, AuditLog
)
from backend.app.anomaly.risk_engine import calculate_investigation_priority

def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    print("Seeding ProcureShield AI database...")
    
    # 1. Users
    investigator = User(
        name="Sarah Chen",
        email="sarah.chen@procureshield.gov",
        hashed_password=get_password_hash("password123"),
        role="INVESTIGATOR",
        department="Special Investigations Unit",
        avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"
    )
    official = User(
        name="Rajiv Menon",
        email="rajiv.menon@gov.in",
        hashed_password=get_password_hash("password123"),
        role="OFFICIAL",
        department="Ministry of Road Transport & Highways",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"
    )
    researcher = User(
        name="Dr. Alisha Roy",
        email="alisha.roy@transparency.org",
        hashed_password=get_password_hash("password123"),
        role="RESEARCHER",
        department="Open Procurement Policy Lab",
        avatar_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80"
    )
    citizen_rohan = User(
        name="Rohan Verma",
        email="rohan.verma@citizen.in",
        hashed_password=get_password_hash("password123"),
        role="CITIZEN",
        department=None,
        avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"
    )
    citizen_priya = User(
        name="Priya Mehta",
        email="priya.mehta@citizen.in",
        hashed_password=get_password_hash("password123"),
        role="CITIZEN",
        department=None,
        avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80"
    )
    citizen_ananya = User(
        name="Ananya Singh",
        email="ananya.singh@citizen.in",
        hashed_password=get_password_hash("password123"),
        role="CITIZEN",
        department=None,
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
    )
    
    db.add_all([investigator, official, researcher, citizen_rohan, citizen_priya, citizen_ananya])
    db.commit()

    # Reviewer Profiles (PRD Section 12 & 13)
    db.add(ReviewerProfile(
        user_id=citizen_rohan.id,
        reputation_score=94.0,
        total_reports=156,
        verified_reports=142,
        false_reports=2,
        rank=1,
        badges="#1 Citizen Reviewer,Trusted Reviewer,Top Investigator Supporter"
    ))
    db.add(ReviewerProfile(
        user_id=citizen_priya.id,
        reputation_score=92.0,
        total_reports=142,
        verified_reports=129,
        false_reports=3,
        rank=2,
        badges="Evidence Contributor,Trusted Reviewer"
    ))
    db.add(ReviewerProfile(
        user_id=citizen_ananya.id,
        reputation_score=90.0,
        total_reports=128,
        verified_reports=118,
        false_reports=4,
        rank=3,
        badges="Community Watcher,Evidence Contributor"
    ))
    db.commit()

    # 2. Vendors (PRD Section 44 Flagship + Acceptance Tests)
    v_buildright = Vendor(
        name="BuildRight Infrastructure Ltd.",
        registration_number="REG-2015-BR882",
        tax_id="GSTIN-07AABCB8821Z1",
        address="402 Synergy Business Tower, Sector 62",
        city="Noida",
        state="Uttar Pradesh",
        category="Roads",
        win_rate=0.90,  # 9 of 10 wins
        total_contracts=10,
        total_contract_value=24500000.0,
        avg_delay_days=105.0,
        quality_score=52.0,
        complaint_rate=3.7,
        maintenance_cost_ratio=2.4,
        risk_level="CRITICAL"
    )
    v_apex = Vendor(
        name="Apex Infra Projects Ltd.",
        registration_number="REG-2016-AP419",
        tax_id="GSTIN-07AABCA4192Z3",
        address="120 Barakhamba Road, Connaught Place",
        city="New Delhi",
        state="Delhi",
        category="Bridges",
        win_rate=0.88,
        total_contracts=8,
        total_contract_value=32000000.0,
        avg_delay_days=45.0,
        quality_score=64.0,
        complaint_rate=2.1,
        maintenance_cost_ratio=1.9,
        risk_level="HIGH"
    )
    v_skyline = Vendor(
        name="Skyline Civil Works Pvt Ltd.",
        registration_number="REG-2017-SC903",
        tax_id="GSTIN-07AABCS9033Z5",
        address="402 Synergy Business Tower, Sector 62",  # SAME ADDRESS as BuildRight!
        city="Noida",
        state="Uttar Pradesh",
        category="Roads",
        win_rate=0.35,
        total_contracts=4,
        total_contract_value=9800000.0,
        avg_delay_days=30.0,
        quality_score=78.0,
        complaint_rate=0.8,
        maintenance_cost_ratio=1.1,
        risk_level="MEDIUM"
    )
    v_horizon = Vendor(
        name="Horizon Urban Engineering",
        registration_number="REG-2018-HU102",
        tax_id="GSTIN-27AABCH1024Z7",
        address="88 Nariman Point, Marine Drive",
        city="Mumbai",
        state="Maharashtra",
        category="Water/Sanitation",
        win_rate=0.42,
        total_contracts=6,
        total_contract_value=18000000.0,
        avg_delay_days=25.0,
        quality_score=82.0,
        complaint_rate=0.5,
        maintenance_cost_ratio=1.0,
        risk_level="LOW"
    )
    v_civic = Vendor(
        name="CivicBuild Solutions",
        registration_number="REG-2019-CB331",
        tax_id="GSTIN-27AABCC3315Z9",
        address="88 Nariman Point, Marine Drive",  # SAME ADDRESS as Horizon!
        city="Mumbai",
        state="Maharashtra",
        category="Water/Sanitation",
        win_rate=0.78,
        total_contracts=7,
        total_contract_value=21000000.0,
        avg_delay_days=85.0,
        quality_score=58.0,
        complaint_rate=4.2,
        maintenance_cost_ratio=2.5,
        risk_level="HIGH"
    )
    v_benchmark1 = Vendor(
        name="National Highway Builders Ltd.",
        registration_number="REG-2012-NH001",
        tax_id="GSTIN-07AABCN0011Z2",
        address="Plot 14 Institutional Area",
        city="New Delhi",
        state="Delhi",
        category="Roads",
        win_rate=0.28,
        total_contracts=15,
        total_contract_value=55000000.0,
        avg_delay_days=12.0,
        quality_score=91.0,
        complaint_rate=0.2,
        maintenance_cost_ratio=0.95,
        risk_level="LOW"
    )
    v_benchmark2 = Vendor(
        name="Shakti Construction Co.",
        registration_number="REG-2014-SC554",
        tax_id="GSTIN-06AABCS5542Z8",
        address="Industrial Estate, Phase 3",
        city="Gurugram",
        state="Haryana",
        category="Healthcare",
        win_rate=0.25,
        total_contracts=12,
        total_contract_value=42000000.0,
        avg_delay_days=8.0,
        quality_score=94.0,
        complaint_rate=0.1,
        maintenance_cost_ratio=0.90,
        risk_level="LOW"
    )
    
    db.add_all([v_buildright, v_apex, v_skyline, v_horizon, v_civic, v_benchmark1, v_benchmark2])
    db.commit()

    # Vendor Relationships (PRD Section 20 & 44)
    db.add(VendorRelationship(
        source_vendor_id=v_buildright.id,
        target_vendor_id=v_apex.id,
        relationship_type="SHARED_DIRECTOR",
        entity_name="Vikram Malhotra (DIN: 08472910)",
        evidence_details="Ministry of Corporate Affairs filing shows Vikram Malhotra serving as active Director in both BuildRight Infrastructure and Apex Infra Projects.",
        confidence_score=0.98
    ))
    db.add(VendorRelationship(
        source_vendor_id=v_buildright.id,
        target_vendor_id=v_skyline.id,
        relationship_type="SHARED_ADDRESS",
        entity_name="402 Synergy Business Tower, Sector 62, Noida",
        evidence_details="Both companies registered under identical commercial office suite and shared telephone exchange.",
        confidence_score=0.95
    ))
    db.add(VendorRelationship(
        source_vendor_id=v_buildright.id,
        target_vendor_id=v_apex.id,
        relationship_type="FREQUENT_CO_BIDDER",
        entity_name="Joint Highway Tenders 2022-2024",
        evidence_details="Bidded together in 9 consecutive state highway tenders with consistent 1.2% - 2.0% pricing spread.",
        confidence_score=0.92
    ))
    db.add(VendorRelationship(
        source_vendor_id=v_civic.id,
        target_vendor_id=v_horizon.id,
        relationship_type="SHARED_DIRECTOR",
        entity_name="Sunil Singhania (DIN: 07198244)",
        evidence_details="Directorship cross-holding recorded in state registrar filings.",
        confidence_score=0.96
    ))
    db.commit()

    # 3. Tenders, Bids, Contracts, Projects
    
    # ── CASE 1 (FLAGSHIP): NH-21 Rural Road (PRD Section 44) ──
    t_nh21 = Tender(
        tender_code="TN-2023-ROAD-042",
        title="Widening & Paving of NH-21 Rural Connecting Road (12 km)",
        description="Civil works comprising base widening, asphalt laying, and storm drainage culverts for 12 km rural corridor.",
        department="Public Works Department (PWD)",
        category="Roads",
        estimated_value=1720000.0,
        publication_date=datetime.utcnow() - timedelta(days=360),
        submission_deadline=datetime.utcnow() - timedelta(days=330),
        status="AWARDED",
        winning_vendor_id=v_buildright.id,
        winning_bid_amount=2000000.0, # ₹2.0M vs ₹1.72M benchmark (+16.3% deviation)
        location="NH-21 Rural Sector, Himachal Pradesh"
    )
    db.add(t_nh21)
    db.commit()

    # Bids for NH-21: Suspicious bid clustering
    b1 = Bid(tender_id=t_nh21.id, vendor_id=v_buildright.id, bid_amount=2000000.0, submission_time=t_nh21.submission_deadline - timedelta(minutes=14), rank=1, is_winning=True, technical_score=88.0, pricing_deviation_pct=16.3)
    b2 = Bid(tender_id=t_nh21.id, vendor_id=v_apex.id, bid_amount=2024000.0, submission_time=t_nh21.submission_deadline - timedelta(minutes=11), rank=2, is_winning=False, technical_score=86.0, pricing_deviation_pct=17.7)
    b3 = Bid(tender_id=t_nh21.id, vendor_id=v_skyline.id, bid_amount=2048000.0, submission_time=t_nh21.submission_deadline - timedelta(minutes=8), rank=3, is_winning=False, technical_score=84.0, pricing_deviation_pct=19.1)
    db.add_all([b1, b2, b3])
    db.commit()

    c_nh21 = Contract(
        contract_code="CNT-2023-NH21-008",
        tender_id=t_nh21.id,
        vendor_id=v_buildright.id,
        contracted_amount=2000000.0,
        sign_date=datetime.utcnow() - timedelta(days=320),
        planned_start_date=datetime.utcnow() - timedelta(days=310),
        planned_completion_date=datetime.utcnow() - timedelta(days=130), # 180 days planned
        actual_completion_date=datetime.utcnow() - timedelta(days=25),   # 285 days actual
        status="COMPLETED"
    )
    db.add(c_nh21)
    db.commit()

    p_nh21 = Project(
        contract_id=c_nh21.id,
        name="NH-21 Rural Road (12 km)",
        description="Asphalt pavement expansion and culvert drainage between Village Rampur and Highway Junction 4.",
        category="Roads",
        department="Public Works Department (PWD)",
        location_name="NH-21 Sector 4, Mandi District",
        latitude=31.5892,
        longitude=76.9182,
        planned_duration_days=180,
        actual_duration_days=285,
        delay_days=105, # +105 days delay
        planned_cost=2000000.0,
        actual_cost=2380000.0,
        cost_overrun_pct=19.0,
        execution_status="COMPLETED",
        quality_status="CRITICAL_FAILURE"
    )
    db.add(p_nh21)
    db.commit()

    # Inspections for NH-21
    db.add(Inspection(
        project_id=p_nh21.id,
        inspection_date=datetime.utcnow() - timedelta(days=80),
        inspector_name="K. V. Raman",
        inspector_agency="State Quality Control Bureau",
        result="FAILED",
        specification_deviations="Sub-base bitumen thickness measured 42mm versus 65mm contracted specification. Premature longitudinal surface cracking observed.",
        notes="Recommend structural core sampling and contractor remediation notice."
    ))

    # Quality record
    db.add(QualityRecord(
        project_id=p_nh21.id,
        defect_category="Asphalt Specification Deviation",
        severity="CRITICAL",
        description="Bituminous surface thickness below IRC-37 mandatory design standard; aggregate detachment in multiple sections.",
        detected_date=datetime.utcnow() - timedelta(days=75),
        resolved=False
    ))

    # Citizen feedback for NH-21 (37 verified complaints)
    complaint_titles = [
        ("Severe pothole cluster near KM-4 marker causing bike accidents", "ROAD_QUALITY", 1, 31.5880, 76.9170, "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop&q=80"),
        ("Road surface peeled off within 3 months of paving", "CONSTRUCTION_DEFECT", 1, 31.5910, 76.9200, "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=600&auto=format&fit=crop&q=80"),
        ("Blocked drainage culvert flooding nearby farmland", "MAINTENANCE_FAILURE", 1, 31.5860, 76.9150, "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&auto=format&fit=crop&q=80"),
        ("Dangerous shoulder drop-off with zero safety barriers", "SAFETY_HAZARD", 2, 31.5930, 76.9230, "https://images.unsplash.com/photo-1508873696983-2df5293cb325?w=600&auto=format&fit=crop&q=80"),
        ("Cracks spreading across entire 2 km stretch between Village Rampur", "ROAD_QUALITY", 1, 31.5895, 76.9185, "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop&q=80")
    ]
    for idx, (ctitle, ccat, crating, clat, clng, cmedia) in enumerate(complaint_titles, start=1):
        cmp = Complaint(
            project_id=p_nh21.id,
            citizen_id=citizen_rohan.id if idx % 2 == 1 else citizen_priya.id,
            title=ctitle,
            description=f"{ctitle}. Delivered asphalt quality is substandard and deteriorating rapidly under light monsoon rain.",
            category=ccat,
            rating=crating,
            location="NH-21 Rural Corridor, Mandi District",
            latitude=clat,
            longitude=clng,
            status="VERIFIED",
            reviewer_credibility_weight=0.94 if idx % 2 == 1 else 0.92
        )
        db.add(cmp)
        db.commit()
        db.refresh(cmp)
        db.add(ComplaintMedia(complaint_id=cmp.id, media_url=cmedia, media_type="IMAGE", description="Citizen evidence photo"))
        
    # Additional 32 synthetic complaints to reach 37 verified reports as in PRD Section 44
    for i in range(6, 38):
        cmp_extra = Complaint(
            project_id=p_nh21.id,
            citizen_id=citizen_ananya.id,
            title=f"Surface degradation report section #{i}",
            description="Surface aggregate detachment and edge raveling observed along rural carriageway.",
            category="ROAD_QUALITY",
            rating=1,
            location=f"NH-21 KM-{i%12 + 1}",
            latitude=31.5892 + (i * 0.0005),
            longitude=76.9182 + (i * 0.0004),
            status="VERIFIED",
            reviewer_credibility_weight=0.90
        )
        db.add(cmp_extra)
    db.commit()

    # Maintenance records for NH-21 (2.4x benchmark)
    db.add(MaintenanceRecord(
        project_id=p_nh21.id,
        maintenance_date=datetime.utcnow() - timedelta(days=40),
        cost=240000.0,
        vendor_id=v_buildright.id,
        maintenance_type="EMERGENCY",
        benchmark_cost_ratio=2.4,
        description="Emergency pothole filling and surface resealing after early asphalt disintegration."
    ))
    db.add(MaintenanceRecord(
        project_id=p_nh21.id,
        maintenance_date=datetime.utcnow() - timedelta(days=15),
        cost=175000.0,
        vendor_id=v_buildright.id,
        maintenance_type="STRUCTURAL_REPAIR",
        benchmark_cost_ratio=2.4,
        description="Reconstruction of failed culvert retaining wall and subgrade stabilization."
    ))
    db.commit()

    # ── CASE 2: Acceptance Test 2 — Metro Rail Span 4B (40% Price Anomaly) ──
    t_metro = Tender(
        tender_code="TN-2023-METRO-109",
        title="Elevated Viaduct Span Construction (Metro Line 4B)",
        description="Prefabricated segmental girder erection and track plinth casting for 3.5 km elevated corridor.",
        department="Urban Transport Corporation",
        category="Bridges",
        estimated_value=3000000.0,
        publication_date=datetime.utcnow() - timedelta(days=240),
        submission_deadline=datetime.utcnow() - timedelta(days=210),
        status="AWARDED",
        winning_vendor_id=v_apex.id,
        winning_bid_amount=4200000.0, # 40% above 3.0M peer median!
        location="Metro Corridor West, Delhi NCR"
    )
    db.add(t_metro)
    db.commit()
    db.add(Bid(tender_id=t_metro.id, vendor_id=v_apex.id, bid_amount=4200000.0, rank=1, is_winning=True, technical_score=92.0, pricing_deviation_pct=40.0))
    c_metro = Contract(
        contract_code="CNT-2023-METRO-4B",
        tender_id=t_metro.id,
        vendor_id=v_apex.id,
        contracted_amount=4200000.0,
        planned_start_date=datetime.utcnow() - timedelta(days=200),
        planned_completion_date=datetime.utcnow() - timedelta(days=20),
        status="ACTIVE"
    )
    db.add(c_metro)
    db.commit()
    p_metro = Project(
        contract_id=c_metro.id,
        name="Metro Elevated Viaduct Span 4B",
        description="Segmental girder installation across 3.5 km congested urban corridor.",
        category="Bridges",
        department="Urban Transport Corporation",
        location_name="Dwarka Expressway Junction, New Delhi",
        latitude=28.5355,
        longitude=77.0588,
        planned_duration_days=180,
        actual_duration_days=220,
        delay_days=40,
        planned_cost=3000000.0,
        actual_cost=4200000.0,
        cost_overrun_pct=40.0,
        execution_status="DELAYED",
        quality_status="DEFECTS_REPORTED"
    )
    db.add(p_metro)
    db.commit()

    # ── CASE 3: Acceptance Test 6 & 8 — Ward 14 Stormwater Drainage (Maintenance 2.5x + 50 Complaints) ──
    t_drain = Tender(
        tender_code="TN-2023-DRAIN-018",
        title="Ward 14 Underground Stormwater Trunk Line & Pumping Sump",
        description="Construction of 4.2 km reinforced concrete trunk stormwater conduit.",
        department="Municipal Corporation Sanitation Dept",
        category="Water/Sanitation",
        estimated_value=1500000.0,
        publication_date=datetime.utcnow() - timedelta(days=300),
        submission_deadline=datetime.utcnow() - timedelta(days=270),
        status="AWARDED",
        winning_vendor_id=v_civic.id,
        winning_bid_amount=1780000.0,
        location="Ward 14 Industrial Area, Mumbai"
    )
    db.add(t_drain)
    db.commit()
    db.add(Bid(tender_id=t_drain.id, vendor_id=v_civic.id, bid_amount=1780000.0, rank=1, is_winning=True, technical_score=87.0, pricing_deviation_pct=18.6))
    db.add(Bid(tender_id=t_drain.id, vendor_id=v_horizon.id, bid_amount=1810000.0, rank=2, is_winning=False, technical_score=85.0, pricing_deviation_pct=20.6))
    c_drain = Contract(
        contract_code="CNT-2023-DRAIN-018",
        tender_id=t_drain.id,
        vendor_id=v_civic.id,
        contracted_amount=1780000.0,
        planned_start_date=datetime.utcnow() - timedelta(days=260),
        planned_completion_date=datetime.utcnow() - timedelta(days=120),
        status="COMPLETED"
    )
    db.add(c_drain)
    db.commit()
    p_drain = Project(
        contract_id=c_drain.id,
        name="Ward 14 Stormwater Trunk System",
        description="Trunk drainage pipeline and pump sump serving municipal low-lying zones.",
        category="Water/Sanitation",
        department="Municipal Corporation Sanitation Dept",
        location_name="Kurla Industrial Estate, Mumbai",
        latitude=19.0728,
        longitude=72.8796,
        planned_duration_days=140,
        actual_duration_days=225,
        delay_days=85,
        planned_cost=1500000.0,
        actual_cost=1950000.0,
        cost_overrun_pct=30.0,
        execution_status="COMPLETED",
        quality_status="CRITICAL_FAILURE"
    )
    db.add(p_drain)
    db.commit()

    # Maintenance 2.5x benchmark
    db.add(MaintenanceRecord(
        project_id=p_drain.id,
        maintenance_date=datetime.utcnow() - timedelta(days=30),
        cost=320000.0,
        vendor_id=v_civic.id,
        maintenance_type="EMERGENCY",
        benchmark_cost_ratio=2.5,
        description="Emergency desilting and collapsed conduit excavation following monsoon inundation."
    ))

    # 52 verified citizen complaints (PRD Acceptance Test 8)
    for i in range(1, 53):
        db.add(Complaint(
            project_id=p_drain.id,
            citizen_id=citizen_rohan.id if i % 2 == 0 else citizen_priya.id,
            title=f"Severe street overflow & collapsed sewer lid #{i}",
            description="Untreated stormwater backflow overflowing into residential basements and storefronts.",
            category="MAINTENANCE_FAILURE",
            rating=1,
            location="Ward 14 Kurla West",
            latitude=19.0728 + (i * 0.0003),
            longitude=72.8796 + (i * 0.0002),
            status="VERIFIED",
            reviewer_credibility_weight=0.92
        ))
    db.commit()

    # ── CASE 4: Acceptance Test 5 — Solar Microgrid Phase 2 (110 Days Late) ──
    t_solar = Tender(
        tender_code="TN-2023-SOLAR-066",
        title="Solar Rooftop Microgrid & Battery Storage Installation",
        description="500 kWp distributed solar generation across district administrative offices.",
        department="Renewable Energy Development Agency",
        category="Power & Energy",
        estimated_value=1200000.0,
        publication_date=datetime.utcnow() - timedelta(days=280),
        submission_deadline=datetime.utcnow() - timedelta(days=250),
        status="AWARDED",
        winning_vendor_id=v_buildright.id,
        winning_bid_amount=1220000.0,
        location="Solan District Complex"
    )
    db.add(t_solar)
    db.commit()
    db.add(Bid(tender_id=t_solar.id, vendor_id=v_buildright.id, bid_amount=1220000.0, rank=1, is_winning=True, technical_score=85.0, pricing_deviation_pct=1.6))
    c_solar = Contract(
        contract_code="CNT-2023-SOLAR-066",
        tender_id=t_solar.id,
        vendor_id=v_buildright.id,
        contracted_amount=1220000.0,
        planned_start_date=datetime.utcnow() - timedelta(days=240),
        planned_completion_date=datetime.utcnow() - timedelta(days=120),
        status="COMPLETED"
    )
    db.add(c_solar)
    db.commit()
    p_solar = Project(
        contract_id=c_solar.id,
        name="Solar Rooftop Microgrid Phase 2",
        description="500 kWp rooftop solar installation with battery storage bank.",
        category="Power & Energy",
        department="Renewable Energy Development Agency",
        location_name="Solan Administrative Complex",
        latitude=30.9084,
        longitude=77.0999,
        planned_duration_days=120,
        actual_duration_days=230, # +110 days late!
        delay_days=110,
        planned_cost=1200000.0,
        actual_cost=1240000.0,
        cost_overrun_pct=3.3,
        execution_status="COMPLETED",
        quality_status="SATISFACTORY"
    )
    db.add(p_solar)
    db.commit()

    # ── CASE 5: Acceptance Test 7 — Primary Healthcare Clinic (1 Single Complaint -> Low Influence) ──
    t_clinic = Tender(
        tender_code="TN-2023-HEALTH-005",
        title="Community Health Center Modernization & OPD Expansion",
        description="Renovation of outpatient clinic and maternal health wing.",
        department="Department of Health & Family Welfare",
        category="Healthcare",
        estimated_value=950000.0,
        publication_date=datetime.utcnow() - timedelta(days=200),
        submission_deadline=datetime.utcnow() - timedelta(days=180),
        status="AWARDED",
        winning_vendor_id=v_benchmark2.id,
        winning_bid_amount=940000.0,
        location="Karnal Health Center"
    )
    db.add(t_clinic)
    db.commit()
    db.add(Bid(tender_id=t_clinic.id, vendor_id=v_benchmark2.id, bid_amount=940000.0, rank=1, is_winning=True, technical_score=95.0, pricing_deviation_pct=-1.0))
    c_clinic = Contract(
        contract_code="CNT-2023-HEALTH-005",
        tender_id=t_clinic.id,
        vendor_id=v_benchmark2.id,
        contracted_amount=940000.0,
        planned_start_date=datetime.utcnow() - timedelta(days=170),
        planned_completion_date=datetime.utcnow() - timedelta(days=50),
        status="COMPLETED"
    )
    db.add(c_clinic)
    db.commit()
    p_clinic = Project(
        contract_id=c_clinic.id,
        name="Community Health Center OPD Wing",
        description="Modernization of 40-bed maternal and infant outpatient facility.",
        category="Healthcare",
        department="Department of Health & Family Welfare",
        location_name="Karnal Civil Hospital Complex",
        latitude=29.6857,
        longitude=76.9905,
        planned_duration_days=120,
        actual_duration_days=124,
        delay_days=4,
        planned_cost=950000.0,
        actual_cost=945000.0,
        cost_overrun_pct=0.0,
        execution_status="COMPLETED",
        quality_status="SATISFACTORY"
    )
    db.add(p_clinic)
    db.commit()
    # Exactly 1 citizen complaint
    db.add(Complaint(
        project_id=p_clinic.id,
        citizen_id=citizen_ananya.id,
        title="Water tap in waiting area needs minor plumbing repair",
        description="One faucet in patient waiting room has a slow drip. Rest of the facility is clean and well-built.",
        category="MAINTENANCE_FAILURE",
        rating=4,
        location="Karnal Health Center OPD",
        latitude=29.6857,
        longitude=76.9905,
        status="VERIFIED",
        reviewer_credibility_weight=0.90
    ))
    db.commit()

    # ── CASE 6: Model High School Construction (Clean Benchmark Case) ──
    t_school = Tender(
        tender_code="TN-2023-EDU-022",
        title="Construction of Model Senior Secondary Smart School",
        description="18 classrooms, science laboratory, and sports field.",
        department="Department of School Education",
        category="Education",
        estimated_value=2200000.0,
        publication_date=datetime.utcnow() - timedelta(days=340),
        submission_deadline=datetime.utcnow() - timedelta(days=310),
        status="AWARDED",
        winning_vendor_id=v_benchmark1.id,
        winning_bid_amount=2180000.0,
        location="Sector 18 Model Town"
    )
    db.add(t_school)
    db.commit()
    db.add(Bid(tender_id=t_school.id, vendor_id=v_benchmark1.id, bid_amount=2180000.0, rank=1, is_winning=True, technical_score=94.0, pricing_deviation_pct=-0.9))
    c_school = Contract(
        contract_code="CNT-2023-EDU-022",
        tender_id=t_school.id,
        vendor_id=v_benchmark1.id,
        contracted_amount=2180000.0,
        planned_start_date=datetime.utcnow() - timedelta(days=300),
        planned_completion_date=datetime.utcnow() - timedelta(days=100),
        status="COMPLETED"
    )
    db.add(c_school)
    db.commit()
    p_school = Project(
        contract_id=c_school.id,
        name="Model Senior Secondary Smart School",
        description="Composite school building featuring solar energy, rainwater harvesting, and smart classrooms.",
        category="Education",
        department="Department of School Education",
        location_name="Sector 18, Chandigarh",
        latitude=30.7333,
        longitude=76.7794,
        planned_duration_days=200,
        actual_duration_days=195,
        delay_days=0,
        planned_cost=2200000.0,
        actual_cost=2180000.0,
        cost_overrun_pct=0.0,
        execution_status="COMPLETED",
        quality_status="SATISFACTORY"
    )
    db.add(p_school)
    db.commit()

    # 4. Compute Risk Scores & Generate Alerts for all Tenders
    tenders_to_score = [
        (t_nh21, v_buildright, p_nh21, "CASE-2024-1042", investigator.id),
        (t_metro, v_apex, p_metro, "CASE-2024-1088", None),
        (t_drain, v_civic, p_drain, "CASE-2024-1104", investigator.id),
        (t_solar, v_buildright, p_solar, "CASE-2024-1152", None),
        (t_clinic, v_benchmark2, p_clinic, "CASE-2024-1180", None),
        (t_school, v_benchmark1, p_school, "CASE-2024-1205", None)
    ]

    all_vendors = db.query(Vendor).all()

    for tender, vendor, project, case_code, assigned_id in tenders_to_score:
        peer_vendors = [v for v in all_vendors if v.category == vendor.category]
        eval_result = calculate_investigation_priority(tender, vendor, project, db, peer_vendors)
        
        alert = Alert(
            case_code=case_code,
            tender_id=tender.id,
            vendor_id=vendor.id,
            project_id=project.id if project else None,
            priority_score=eval_result["priority_score"],
            priority_tier=eval_result["priority_tier"],
            status="NEW" if not assigned_id else "UNDER_REVIEW",
            assigned_investigator_id=assigned_id,
            main_signal=eval_result["main_signal"],
            procurement_risk=eval_result["procurement_risk"],
            network_risk=eval_result["network_risk"],
            price_risk=eval_result["price_risk"],
            execution_risk=eval_result["execution_risk"],
            quality_risk=eval_result["quality_risk"],
            feedback_risk=eval_result["feedback_risk"],
            maintenance_risk=eval_result["maintenance_risk"],
            confidence_score=eval_result["confidence_score"]
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        # Add granular risk signals
        for sig in eval_result["signals"]:
            db.add(RiskSignal(
                alert_id=alert.id,
                signal_category=sig["category"],
                title=sig["title"],
                description=sig["description"],
                severity=sig.get("severity", "MEDIUM"),
                confidence=sig.get("confidence", 90.0),
                peer_benchmark_info=sig.get("benchmark"),
                weight=1.0
            ))
            
        # Add seed notes for flagship NH-21 case
        if case_code == "CASE-2024-1042":
            db.add(InvestigationNote(
                alert_id=alert.id,
                author_id=investigator.id,
                note_text="Initial triage completed. Corporate registry cross-check confirmed Vikram Malhotra directorship overlap with Apex Infra. Asphalt sample requested from PWD Mandi sub-division."
            ))
            db.add(InvestigationNote(
                alert_id=alert.id,
                author_id=investigator.id,
                note_text="Citizen reviewer Rohan Verma has provided 5 high-resolution geo-tagged photographs showing extensive base pavement disintegration at KM-4."
            ))
            
        # Add audit log entry
        db.add(AuditLog(
            user_id=investigator.id if assigned_id else None,
            user_email=investigator.email if assigned_id else "system@procureshield.ai",
            action=f"Generated investigation alert with priority {alert.priority_score}/100 ({alert.priority_tier})",
            case_code=case_code,
            previous_state=None,
            new_state=alert.status,
            ip_address="127.0.0.1"
        ))
        db.commit()

    print("Database seeded successfully with realistic procurement lifecycle cases!")
    db.close()

if __name__ == "__main__":
    seed_database()
