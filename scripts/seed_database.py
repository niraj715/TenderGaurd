"""
ProcureShield AI — Database Seeding Script
Populates the database from generated CSV datasets:
- vendors (50)
- tenders (500)
- bids (2,968)
- awards (500)
- contracts (500)
- vendor_relationships (18)
- vendor_together_participation (1,225)
- benchmark_cases (45)
- investigations (500)
- risk_signals (computed C1–C20 indicators)
- users & reviewer profiles
- projects & citizen feedback
"""

import os
import csv
import json
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.core.database import engine, SessionLocal, Base
from backend.app.core.security import get_password_hash
from backend.app.models.entities import (
    User, ReviewerProfile, ReviewerContribution,
    Vendor, VendorRelationship, VendorTogetherParticipation,
    Tender, Bid, Award, Contract,
    Investigation, RiskSignal, InvestigationNote, BenchmarkCase,
    Complaint, ComplaintMedia, Project, Inspection, QualityRecord, MaintenanceRecord, AuditLog
)
from backend.app.anomaly.c_indicators import AnomalyIndicatorEngine, is_true

DATA_DIR = "data/generated"

def load_csv(filename: str):
    path = os.path.join(DATA_DIR, filename)
    with open(path, mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def parse_dt(s: str):
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def seed():
    print("Dropping and recreating all tables with fresh schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        print("Clearing existing data...")
        db.query(AuditLog).delete()
        db.query(InvestigationNote).delete()
        db.query(RiskSignal).delete()
        db.query(Investigation).delete()
        db.query(BenchmarkCase).delete()
        db.query(MaintenanceRecord).delete()
        db.query(QualityRecord).delete()
        db.query(Inspection).delete()
        db.query(Complaint).delete()
        db.query(Project).delete()
        db.query(Contract).delete()
        db.query(Award).delete()
        db.query(Bid).delete()
        db.query(Tender).delete()
        db.query(VendorTogetherParticipation).delete()
        db.query(VendorRelationship).delete()
        db.query(Vendor).delete()
        db.query(ReviewerContribution).delete()
        db.query(ReviewerProfile).delete()
        db.query(User).delete()
        db.commit()

        # 1. SEED USERS & PERSONAS (ONLY INVESTIGATOR & CITIZEN)
        print("Seeding Users & Personas...")
        users_data = [
            {"name": "Sarah Chen", "email": "sarah.chen@procureshield.gov.in", "role": "INVESTIGATOR", "department": "Forensic Audit & Vigilance Cell"},
            {"name": "Rohan Verma", "email": "rohan.verma@citizenwatch.org", "role": "CITIZEN", "department": "Public Infrastructure Watch"},
            {"name": "Priya Mehta", "email": "priya.mehta@citizen.in", "role": "CITIZEN", "department": "Urban Civic Oversight"},
            {"name": "Ananya Singh", "email": "ananya.singh@citizen.in", "role": "CITIZEN", "department": "Rural Road Monitor"},
            {"name": "Vikram Rao", "email": "vikram.rao@citizen.in", "role": "CITIZEN", "department": "Green Infrastructure Watch"},
            {"name": "Neha Kapoor", "email": "neha.kapoor@citizen.in", "role": "CITIZEN", "department": "Civic Transparency Forum"},
            {"name": "Niraj Kumar", "email": "nirajkumar1010a@gmail.com", "role": "INVESTIGATOR", "department": "Central Procurement Intelligence Directorate"},
        ]

        user_objs = {}
        for u in users_data:
            user = User(
                name=u["name"],
                email=u["email"],
                hashed_password=get_password_hash("password123"),
                role=u["role"],
                department=u["department"],
                avatar_url=f"https://api.dicebear.com/7.x/bottts/svg?seed={u['name']}"
            )
            db.add(user)
            db.flush()
            user_objs[u["email"]] = user

            if u["role"] == "CITIZEN":
                rank_map = {
                    "rohan.verma@citizenwatch.org": (1, 156, 96.5, "Master Auditor"),
                    "priya.mehta@citizen.in": (2, 142, 94.2, "Senior Watcher"),
                    "ananya.singh@citizen.in": (3, 128, 92.0, "Verified Citizen"),
                    "vikram.rao@citizen.in": (4, 96, 88.5, "Community Scout"),
                    "neha.kapoor@citizen.in": (5, 87, 86.0, "Civic Contributor")
                }
                rank, reports, rep, badges = rank_map.get(u["email"], (24, 32, 78.0, "Community Watcher"))
                rev = ReviewerProfile(
                    user_id=user.id,
                    reputation_score=rep,
                    total_reports=reports,
                    verified_reports=int(reports * 0.92),
                    false_reports=int(reports * 0.04),
                    rank=rank,
                    badges=badges
                )
                db.add(rev)

        db.commit()

        # 2. SEED VENDORS
        print("Seeding Vendors...")
        vendors_csv = load_csv("vendors.csv")
        for v in vendors_csv:
            vendor = Vendor(
                vendor_id=v["vendor_id"],
                vendor_name=v["vendor_name"],
                registration_number=v["registration_number"],
                director_id=v["director_id"],
                registered_address=v["registered_address"],
                city=v["city"],
                state=v["state"],
                phone=v["phone"],
                email=v["email"],
                company_type=v["company_type"],
                registration_date=parse_dt(v["registration_date"]),
                industry_category=v["industry_category"]
            )
            db.add(vendor)
        db.commit()

        # 3. SEED VENDOR RELATIONSHIPS & TOGETHER PARTICIPATION
        print("Seeding Vendor Relationships...")
        rels_csv = load_csv("vendor_relationships.csv")
        for r in rels_csv:
            rel = VendorRelationship(
                relationship_id=r["relationship_id"],
                vendor_1=r["vendor_1"],
                vendor_2=r["vendor_2"],
                relationship_type=r["relationship_type"],
                relationship_value=r["relationship_value"],
                confidence=float(r["confidence"])
            )
            db.add(rel)
        db.commit()

        print("Seeding Vendor Together Participation...")
        together_csv = load_csv("together_participation.csv")
        for t in together_csv:
            vtp = VendorTogetherParticipation(
                vendor_1=t["vendor_1"],
                vendor_2=t["vendor_2"],
                together_tender_count=int(t["together_tender_count"]),
                together_percentage=float(t["together_percentage"])
            )
            db.add(vtp)
        db.commit()

        # 4. SEED TENDERS, BIDS, AWARDS, CONTRACTS
        print("Seeding Tenders...")
        tenders_csv = load_csv("tenders.csv")
        for t in tenders_csv:
            tender = Tender(
                tender_id=t["tender_id"],
                buyer_id=t["buyer_id"],
                buyer_name=t["buyer_name"],
                tender_title=t["tender_title"],
                category=t["category"],
                sub_category=t["sub_category"],
                location=t["location"],
                state=t["state"],
                estimated_value_inr=float(t["estimated_value_inr"]),
                procurement_method=t["procurement_method"],
                award_criteria=t["award_criteria"],
                publication_date=parse_dt(t["publication_date"]),
                submission_deadline=parse_dt(t["submission_deadline"]),
                technical_evaluation_date=parse_dt(t["technical_evaluation_date"]),
                financial_evaluation_date=parse_dt(t["financial_evaluation_date"]),
                award_date=parse_dt(t["award_date"]),
                contract_duration_days=int(t["contract_duration_days"]),
                status=t["status"]
            )
            db.add(tender)
        db.commit()

        print("Seeding Bids...")
        bids_csv = load_csv("bids.csv")
        for b in bids_csv:
            bid = Bid(
                bid_id=b["bid_id"],
                tender_id=b["tender_id"],
                vendor_id=b["vendor_id"],
                bid_amount_inr=float(b["bid_amount_inr"]),
                submission_timestamp=parse_dt(b["submission_timestamp"]),
                bid_status=b["bid_status"],
                disqualification_reason=b["disqualification_reason"] or None,
                technical_score=float(b["technical_score"]),
                financial_score=float(b["financial_score"]),
                is_winner=is_true(b["is_winner"])
            )
            db.add(bid)
        db.commit()

        print("Seeding Awards...")
        awards_csv = load_csv("awards.csv")
        for a in awards_csv:
            award = Award(
                award_id=a["award_id"],
                tender_id=a["tender_id"],
                winner_vendor_id=a["winner_vendor_id"],
                awarded_amount_inr=float(a["awarded_amount_inr"]),
                award_date=parse_dt(a["award_date"]),
                award_reason=a["award_reason"]
            )
            db.add(award)
        db.commit()

        print("Seeding Contracts & Projects...")
        contracts_csv = load_csv("contracts.csv")
        for c in contracts_csv:
            contract = Contract(
                contract_id=c["contract_id"],
                tender_id=c["tender_id"],
                vendor_id=c["vendor_id"],
                contract_value_inr=float(c["contract_value_inr"]),
                start_date=parse_dt(c["start_date"]),
                planned_end_date=parse_dt(c["planned_end_date"]),
                actual_end_date=parse_dt(c["actual_end_date"]),
                planned_duration_days=int(c["planned_duration_days"]),
                actual_duration_days=int(c["actual_duration_days"]),
                completion_status=c["completion_status"]
            )
            db.add(contract)

            t_obj = next((t for t in tenders_csv if t["tender_id"] == c["tender_id"]), None)
            proj_name = t_obj["tender_title"] if t_obj else f"Project {c['tender_id']}"
            cat = t_obj["category"] if t_obj else "Civil Infrastructure"
            dept = t_obj["buyer_name"] if t_obj else "PWD"
            loc = t_obj["location"] if t_obj else "Solan"

            proj = Project(
                contract_id=int(c["contract_id"].replace("C", "")),
                tender_id=c["tender_id"],
                name=proj_name,
                description=f"Public infrastructure works: {proj_name}",
                category=cat,
                department=dept,
                location_name=loc,
                planned_duration_days=int(c["planned_duration_days"]),
                actual_duration_days=int(c["actual_duration_days"]),
                planned_cost=float(c["contract_value_inr"]),
                actual_cost=float(c["contract_value_inr"]),
                execution_status=c["completion_status"],
                quality_status="SATISFACTORY" if c["completion_status"] == "COMPLETED" else "ACTION_REQUIRED",
                latitude=float(t_obj.get("latitude", 30.9045)) if t_obj and t_obj.get("latitude") else 30.9045,
                longitude=float(t_obj.get("longitude", 77.0967)) if t_obj and t_obj.get("longitude") else 77.0967
            )
            db.add(proj)

        db.commit()

        # 5. SEED BENCHMARK CASES
        print("Seeding Benchmark Cases...")
        benchmarks_csv = load_csv("benchmark_cases.csv")
        for bm in benchmarks_csv:
            bc = BenchmarkCase(
                tender_id=bm["tender_id"],
                expected_indicator_codes=bm["expected_indicator_codes"],
                scenario_type=bm["scenario_type"],
                benchmark_alert=is_true(bm["benchmark_alert"])
            )
            db.add(bc)
        db.commit()

        # 6. RUN C1–C20 DETECTION ENGINE & SEED INVESTIGATIONS / SIGNALS
        print("Running C1–C20 Detection Engine to populate Investigations & Risk Signals...")
        engine_inst = AnomalyIndicatorEngine(
            tenders_csv, bids_csv, awards_csv, vendors_csv, rels_csv, together_csv
        )

        for t_idx, t in enumerate(tenders_csv, start=1):
            t_id = t["tender_id"]
            eval_res = engine_inst.evaluate_tender(t_id)

            priority_score = eval_res["priority_score"]
            priority_tier = eval_res["priority_tier"]
            indicators = eval_res["detected_indicators"]

            status = "NEW"
            if priority_tier in ("Critical", "High"):
                status = "UNDER_REVIEW" if t_idx % 2 == 0 else "NEW"
            else:
                status = "RESOLVED" if priority_tier == "Low" else "DISMISSED"

            inv = Investigation(
                tender_id=t_id,
                case_code=f"CASE-{t_id}",
                priority_score=priority_score,
                priority_tier=priority_tier,
                status=status,
                signals_count=len(indicators),
                assigned_investigator="Sarah Chen" if priority_tier in ("Critical", "High") else None,
                summary_narrative=f"{len(indicators)} risk indicator(s) identified for human investigation. Automated priority score: {priority_score}/100."
            )
            db.add(inv)
            db.flush()

            for ind in indicators:
                sig = RiskSignal(
                    tender_id=t_id,
                    investigation_id=inv.id,
                    indicator_code=ind["indicator_code"],
                    indicator_name=ind["indicator_name"],
                    title=f"{ind['indicator_code']}: {ind['indicator_name']}",
                    description=ind["explanation"],
                    severity=float(ind["severity"]),
                    confidence=float(ind["confidence"]),
                    evidence_json=json.dumps(ind["evidence"])
                )
                db.add(sig)

            if priority_tier in ("Critical", "High"):
                note = InvestigationNote(
                    investigation_id=inv.id,
                    author_name="Sarah Chen (Lead Investigator)",
                    note_text=f"Preliminary automated screening flagged {len(indicators)} indicators. Evidentiary review initiated under Section 11 PRD guidelines."
                )
                db.add(note)

        db.commit()

        # 7. UPDATE VENDOR AGGREGATED METRICS
        print("Updating vendor statistics...")
        all_vendors = db.query(Vendor).all()
        for v in all_vendors:
            v_awards = db.query(Award).filter(Award.winner_vendor_id == v.vendor_id).all()
            v_bids = db.query(Bid).filter(Bid.vendor_id == v.vendor_id).all()
            v_contracts = db.query(Contract).filter(Contract.vendor_id == v.vendor_id).all()

            v.total_contracts = len(v_awards)
            v.total_contract_value = sum(a.awarded_amount_inr for a in v_awards)
            v.win_rate = round(len(v_awards) / max(1, len(v_bids)), 3)
            
            delays = [c.actual_duration_days - c.planned_duration_days for c in v_contracts if c.actual_duration_days > c.planned_duration_days]
            v.avg_delay_days = round(sum(delays) / max(1, len(delays)), 1) if delays else 0.0

            if v.win_rate >= 0.35 or v.total_contracts >= 20:
                v.risk_level = "HIGH"
            elif v.win_rate >= 0.20:
                v.risk_level = "MEDIUM"
            else:
                v.risk_level = "LOW"

        db.commit()

        # 8. SEED CITIZEN FEEDBACK / COMPLAINTS ACROSS REAL CITIZENS
        print("Seeding Citizen Complaints & Feedback...")
        citizen_users = [
            user_objs["rohan.verma@citizenwatch.org"],
            user_objs["priya.mehta@citizen.in"],
            user_objs["ananya.singh@citizen.in"],
            user_objs["vikram.rao@citizen.in"],
            user_objs["neha.kapoor@citizen.in"]
        ]

        complaint_templates = [
            ("Potholes and bitumen stripping within 60 days of laying", "Materials & Surface Quality", 1, "Solan NH-21 Corridor"),
            ("Delayed embankment compaction causing road edge collapse", "Structural Safety", 2, "Chamba Road Section 3"),
            ("Culvert drainage blocked with debris causing local waterlogging", "Drainage Non-Compliance", 2, "Mandi Bypass Sector 2"),
            ("Over-invoiced material usage observed at asphalt plant", "Billing Discrepancy", 1, "Dharamsala Civil Works"),
            ("Machinery parked idle for 3 weeks while billing milestone submitted", "Execution Delay", 1, "Shimla Highway Package 4"),
            ("Substandard aggregate stone size used for base course", "Specifications Deviation", 1, "Solan Bypass km 14"),
            ("Bridge expansion joint unsealed leading to water seepage", "Workmanship Defect", 2, "Beas River Crossing"),
            ("Unfinished sidewalk pavement left without barricading", "Public Safety", 1, "Kangra Town Ring Road"),
            ("Severe rutting under wheel paths after initial freight traffic", "Materials & Surface Quality", 1, "Baddi Industrial Corridor"),
            ("Retaining gabion wall showing lateral bulging near culvert", "Structural Safety", 2, "Kullu Valley Link km 8"),
            ("Transformer foundation cracked prior to energization", "Electrical Infrastructure", 1, "Parwanoo Power Substation"),
            ("Water main flange connection leaking during hydrostatic test", "Water & Sanitation", 2, "Nahan Water Supply Scheme"),
            ("Cracked drainage slab covers creating hazard for pedestrians", "Public Safety", 2, "Bilaspur City Circle"),
            ("Incomplete street illumination with missing junction boxes", "Electrical Infrastructure", 2, "Hamirpur Urban Expansion"),
            ("Street resurfacing skipped scheduled primer coat", "Workmanship Defect", 1, "Palampur Municipal Roadway"),
            ("Uncovered silt pit causing backflow into agricultural fields", "Drainage Non-Compliance", 1, "Una Canal Alignment"),
            ("Concrete kerb stones crumbling under light vehicular contact", "Materials & Surface Quality", 2, "Sirmaur Highway Sector 1"),
            ("Pre-cast pipe culvert joint separation detected", "Drainage Non-Compliance", 1, "Kinnaur Roadway km 22"),
            ("Road signage missing retro-reflective sheeting per IRC standards", "Public Safety", 3, "Spiti Access Corridor"),
            ("Asphalt binder course laid in rainy conditions violating spec", "Specifications Deviation", 1, "Manali Bypass Package 2")
        ]

        for i in range(1, 41):
            t_id = f"T{i:03d}"
            proj = db.query(Project).filter(Project.tender_id == t_id).first()
            user = citizen_users[i % len(citizen_users)]
            tmpl = complaint_templates[(i - 1) % len(complaint_templates)]
            
            c_date = datetime(2025, 1 + ((i * 2) % 11), 1 + (i % 25), 10, 30)
            comp = Complaint(
                tender_id=t_id,
                project_id=proj.id if proj else 1,
                citizen_id=user.id,
                title=f"{tmpl[0]} (Chainage {i*100}m)",
                description=f"Field audit by verified citizen {user.name}: {tmpl[0]}. Visual inspection verified at site. Photographs archived for public vigilance audit.",
                category=tmpl[1],
                rating=tmpl[2],
                location=f"{tmpl[3]}, {proj.location_name if proj else 'HP'}",
                latitude=proj.latitude if proj else 30.9045,
                longitude=proj.longitude if proj else 77.0967,
                status="VERIFIED" if i % 4 != 0 else "SUBMITTED",
                reviewer_credibility_weight=round(0.85 + ((i % 5) * 0.03), 2),
                created_at=c_date
            )
            db.add(comp)
            db.flush()

            # Add photo media
            media = ComplaintMedia(
                complaint_id=comp.id,
                media_url=f"https://images.unsplash.com/photo-{1580000000000 + i}?auto=format&fit=crop&w=800&q=80",
                media_type="IMAGE",
                description=f"Site verification photo for {t_id}"
            )
            db.add(media)
        db.commit()

        # 9. SEED INSPECTIONS, QUALITY RECORDS & MAINTENANCE FOR ALL 500 PROJECTS
        print("Seeding Inspections, Quality Records & Maintenance across all 500 projects...")
        all_projects = db.query(Project).all()
        from datetime import timedelta

        for p in all_projects:
            t_obj = p.tender
            contract = t_obj.contract if t_obj else None
            inv = t_obj.investigation if t_obj else None
            is_high_risk = inv and inv.priority_tier in ("Critical", "High")

            start = (contract.start_date if contract and contract.start_date else datetime(2024, 4, 1))
            duration = contract.planned_duration_days if contract and contract.planned_duration_days else 180
            
            # Inspection 1: Mid-term inspection
            date_insp1 = start + timedelta(days=max(30, int(duration * 0.45)))
            insp1 = Inspection(
                project_id=p.id,
                inspection_date=date_insp1,
                inspector_name=f"Er. {'R. K. Sharma' if p.id % 2 == 0 else 'Anil Verma'}",
                inspector_agency="HP State Quality Control Cell" if p.id % 2 == 0 else "Independent Quality Monitoring Agency",
                result="ACTION_REQUIRED" if is_high_risk else "PASS",
                specification_deviations="Core compressive strength 21.2 MPa vs 25 MPa specified in Clause 4.2." if is_high_risk else None,
                notes="Compaction density meets MoRTH specification 98.2%. Materials testing passed." if not is_high_risk else "Non-conformance notice issued to contractor. Rectification required within 14 days."
            )
            db.add(insp1)

            # Inspection 2: Final / Pre-commissioning inspection
            date_insp2 = start + timedelta(days=max(60, int(duration * 0.88)))
            insp2 = Inspection(
                project_id=p.id,
                inspection_date=date_insp2,
                inspector_name="Er. S. Chauhan (Chief Quality Assessor)",
                inspector_agency="Public Works Quality Directorate",
                result="PASS",
                specification_deviations=None,
                notes="Comprehensive site audit completed. Punch list items cleared and certified for handover."
            )
            db.add(insp2)

            # Quality Record
            q_cats = ["Materials & Concrete", "Subgrade Compaction", "Drainage Gradient", "Surface Tolerances", "Electrical Safety"]
            q_cat = q_cats[p.id % len(q_cats)]
            q_rec = QualityRecord(
                project_id=p.id,
                defect_category=q_cat,
                severity="HIGH" if is_high_risk else "MEDIUM",
                description=f"Standard QA review on {q_cat}. {'Minor tolerance variance rectified on site.' if not is_high_risk else 'Significant variance flagged for contractor warranty retention.'}",
                detected_date=date_insp1,
                resolved=True if not is_high_risk else False
            )
            db.add(q_rec)

            # Maintenance Record for completed contracts
            if contract and contract.completion_status == "COMPLETED":
                m_date = (contract.actual_end_date or start + timedelta(days=duration)) + timedelta(days=60)
                m_cost = round(p.actual_cost * (0.02 + ((p.id % 4) * 0.01)), 2)
                m_types = [
                    "Routine Surface Resurfacing & Crack Sealing",
                    "Drainage Clearing & Desilting Works",
                    "Pavement Joint Sealant Replacement",
                    "Signage & Barrier Safety Rehabilitation",
                    "Feeder Substation Routine Inspection & Bushing Care"
                ]
                m_type = m_types[p.id % len(m_types)]
                m_ratio = round(1.0 + ((p.id % 5) * 0.25), 2)
                if is_high_risk:
                    m_ratio = round(2.2 + ((p.id % 4) * 0.3), 2)

                maint = MaintenanceRecord(
                    project_id=p.id,
                    maintenance_date=m_date,
                    cost=m_cost,
                    vendor_id=t_obj.award.winner_vendor_id if (t_obj and t_obj.award) else "V001",
                    maintenance_type=m_type,
                    benchmark_cost_ratio=m_ratio,
                    description=f"Post-completion asset maintenance under DLP clause. Cost ratio: {m_ratio}x regional benchmark."
                )
                db.add(maint)

        db.commit()

        print("\n=======================================================")
        print("          DATABASE SEEDING SUCCESSFULLY COMPLETED      ")
        print("=======================================================")
        print(f"Users: {db.query(User).count()}")
        print(f"Vendors: {db.query(Vendor).count()}")
        print(f"Tenders: {db.query(Tender).count()}")
        print(f"Bids: {db.query(Bid).count()}")
        print(f"Awards: {db.query(Award).count()}")
        print(f"Contracts: {db.query(Contract).count()}")
        print(f"Relationships: {db.query(VendorRelationship).count()}")
        print(f"Together Pairs: {db.query(VendorTogetherParticipation).count()}")
        print(f"Benchmark Cases: {db.query(BenchmarkCase).count()}")
        print(f"Investigations: {db.query(Investigation).count()}")
        print(f"Risk Signals: {db.query(RiskSignal).count()}")
        print(f"Complaints: {db.query(Complaint).count()}")
        print("=======================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
