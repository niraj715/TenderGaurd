"""
ProcureShield AI — Deterministic Procurement Dataset Generator
Generates 50 vendors, 500 tenders, ~3,000-4,000 bids, 500 awards, 500 contracts,
15-25 vendor relationships, together participation, and ~35 controlled anomaly benchmark cases.
"""

import os
import csv
import random
from datetime import datetime, timedelta

def generate_dataset(seed: int = 42, output_dir: str = "data/generated"):
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. GENERATE 50 VENDORS
    # -------------------------------------------------------------
    cities_states = [
        ("Shimla", "Himachal Pradesh"),
        ("Solan", "Himachal Pradesh"),
        ("Mandi", "Himachal Pradesh"),
        ("Dharamshala", "Himachal Pradesh"),
        ("Chandigarh", "Punjab"),
        ("Mohali", "Punjab"),
        ("Ludhiana", "Punjab"),
        ("Ambala", "Haryana"),
        ("Panchkula", "Haryana"),
        ("Dehradun", "Uttarakhand"),
        ("Haridwar", "Uttarakhand"),
        ("Jaipur", "Rajasthan"),
        ("New Delhi", "Delhi")
    ]

    categories = [
        "Road Infrastructure",
        "Civil Construction",
        "Water & Sanitation",
        "Electrical & Energy"
    ]

    company_types = ["Private Limited", "Limited", "Partnership", "LLP", "Proprietary"]

    vendor_names_pool = [
        "BuildRight Infra Pvt Ltd", "Apex Constructions Ltd", "Shiva Infra JV", "Skyline Civil Tech",
        "Bharat Earthmovers & Infra", "Krishna Roadways & Infra", "Himalaya Foundations", "Metro Bridges & Civil",
        "Ganga Water Works Ltd", "National Electrics Corp", "Pinnacle Urban Developers", "Surya Power & Infra",
        "Vanguard Engineering Works", "Trident Infrastructure", "Everest Civil Projects", "Zenith Builders Ltd",
        "Omkar Construction Co", "Shree Ram Roadways", "Alliance Structural Engineers", "Prime Civil Consortium",
        "Hilltop Earth Works", "Dynamic Engineering Corp", "Blue Star Infrastructure", "Vertex Project Developers",
        "Royal Civil Builders", "Pioneer Construction Ltd", "Sunrise Contractors & Co", "Global Civil Ventures",
        "Sovereign Infra Projects", "Universal Pipe & Utilities", "Regal Civil Works", "Capital Infrastructure",
        "Modern Builders & Fabricators", "Sigma Infra Solutions", "Alpha Civil Tech", "Theta Construction Group",
        "Falcon Engineering Works", "Sterling Civil Works", "Paramount Infra Projects", "Diamond Civil Contractors",
        "Crown Infrastructure Ltd", "Ruby Builders & Developers", "Emerald Construction", "Sapphire Infra Works",
        "Horizon Civil Ventures", "Matrix Builders Ltd", "Nexus Infrastructure Co", "United Civil Developers",
        "Frontier Engineering Corp", "Supreme Roadways & Bridges"
    ]

    vendors = []
    directors = [f"DIR{1000 + i}" for i in range(40)]  # 40 distinct director IDs for 50 vendors -> 10 shared
    addresses = [f"Plot {i+1}, Industrial Area, Phase {((i%4)+1)}" for i in range(38)]  # some shared addresses

    for i in range(50):
        v_id = f"V{i+1:03d}"
        v_name = vendor_names_pool[i]
        reg_num = f"CIN-U45200HP201{i%10}PTC{100000 + i*137}"
        city, state = cities_states[i % len(cities_states)]
        
        # Planted shared directors & addresses for specific vendors
        if v_id in ["V001", "V002"]:  # BuildRight & Apex share director & address
            dir_id = "DIR1001"
            reg_addr = "Plot 42, Industrial Area, Solan"
            phone = "+91-1792-234501"
            email = f"compliance@{v_name.lower().split()[0]}infra.in"
        elif v_id == "V003":  # Shiva Infra shares address with V001
            dir_id = "DIR1002"
            reg_addr = "Plot 42, Industrial Area, Solan"
            phone = "+91-1792-234502"
            email = "contact@shivainfra.in"
        elif v_id in ["V006", "V012"]:  # Krishna & Vanguard share director
            dir_id = "DIR1006"
            reg_addr = addresses[i % len(addresses)]
            phone = f"+91-172-2789{i:02d}"
            email = f"info@{v_name.lower().split()[0]}.com"
        elif v_id in ["V015", "V016"]:  # Everest & Zenith share phone & email domain
            dir_id = directors[i % len(directors)]
            reg_addr = addresses[i % len(addresses)]
            phone = "+91-177-2804500"
            email = f"bids@everest-zenith-group.com"
        else:
            dir_id = directors[i % len(directors)]
            reg_addr = addresses[i % len(addresses)]
            phone = f"+91-{9800000000 + i*173491}"
            email = f"tenders@{v_name.lower().split()[0]}.in"

        c_type = company_types[i % len(company_types)]
        ind_cat = categories[i % len(categories)]
        reg_date = (datetime(2012, 1, 1) + timedelta(days=i * 73)).strftime("%Y-%m-%d")

        vendors.append({
            "vendor_id": v_id,
            "vendor_name": v_name,
            "registration_number": reg_num,
            "director_id": dir_id,
            "registered_address": reg_addr,
            "city": city,
            "state": state,
            "phone": phone,
            "email": email,
            "company_type": c_type,
            "registration_date": reg_date,
            "industry_category": ind_cat
        })

    # -------------------------------------------------------------
    # 2. VENDOR RELATIONSHIPS (15–25 records)
    # -------------------------------------------------------------
    relationships = [
        {"relationship_id": "R01", "vendor_1": "V001", "vendor_2": "V002", "relationship_type": "shared_director", "relationship_value": "DIR1001 (R. Kumar)", "confidence": 0.99},
        {"relationship_id": "R02", "vendor_1": "V001", "vendor_2": "V002", "relationship_type": "shared_address", "relationship_value": "Plot 42, Industrial Area, Solan", "confidence": 0.98},
        {"relationship_id": "R03", "vendor_1": "V001", "vendor_2": "V003", "relationship_type": "shared_address", "relationship_value": "Plot 42, Industrial Area, Solan", "confidence": 0.96},
        {"relationship_id": "R04", "vendor_1": "V006", "vendor_2": "V012", "relationship_type": "shared_director", "relationship_value": "DIR1006 (S. Singhania)", "confidence": 0.97},
        {"relationship_id": "R05", "vendor_1": "V015", "vendor_2": "V016", "relationship_type": "shared_phone", "relationship_value": "+91-177-2804500", "confidence": 0.95},
        {"relationship_id": "R06", "vendor_1": "V015", "vendor_2": "V016", "relationship_type": "shared_email", "relationship_value": "@everest-zenith-group.com", "confidence": 0.95},
        {"relationship_id": "R07", "vendor_1": "V004", "vendor_2": "V008", "relationship_type": "common_parent", "relationship_value": "Northern Infra Holdings LLP", "confidence": 0.92},
        {"relationship_id": "R08", "vendor_1": "V007", "vendor_2": "V011", "relationship_type": "shared_director", "relationship_value": "DIR1007 (Anil Sharma)", "confidence": 0.96},
        {"relationship_id": "R09", "vendor_1": "V010", "vendor_2": "V014", "relationship_type": "shared_address", "relationship_value": "Plot 14, Industrial Area, Phase 2, Mandi", "confidence": 0.94},
        {"relationship_id": "R10", "vendor_1": "V018", "vendor_2": "V022", "relationship_type": "shared_director", "relationship_value": "DIR1018 (P. Verma)", "confidence": 0.95},
        {"relationship_id": "R11", "vendor_1": "V025", "vendor_2": "V030", "relationship_type": "shared_phone", "relationship_value": "+91-9816044321", "confidence": 0.91},
        {"relationship_id": "R12", "vendor_1": "V033", "vendor_2": "V037", "relationship_type": "common_parent", "relationship_value": "Shivalik Construction Holdings", "confidence": 0.93},
        {"relationship_id": "R13", "vendor_1": "V020", "vendor_2": "V024", "relationship_type": "shared_address", "relationship_value": "Sector 4, Parwanoo, HP", "confidence": 0.94},
        {"relationship_id": "R14", "vendor_1": "V009", "vendor_2": "V013", "relationship_type": "shared_director", "relationship_value": "DIR1009 (M. Gupta)", "confidence": 0.96},
        {"relationship_id": "R15", "vendor_1": "V040", "vendor_2": "V045", "relationship_type": "shared_email", "relationship_value": "admin@apex-united.org", "confidence": 0.90},
        {"relationship_id": "R16", "vendor_1": "V028", "vendor_2": "V032", "relationship_type": "shared_director", "relationship_value": "DIR1028 (R. K. Mehra)", "confidence": 0.97},
        {"relationship_id": "R17", "vendor_1": "V005", "vendor_2": "V019", "relationship_type": "shared_phone", "relationship_value": "+91-1792-221190", "confidence": 0.92},
        {"relationship_id": "R18", "vendor_1": "V041", "vendor_2": "V046", "relationship_type": "common_parent", "relationship_value": "Himalayan Consortium India", "confidence": 0.94}
    ]

    # -------------------------------------------------------------
    # 3. BUYERS & PROCUREMENT SPECIFICATIONS
    # -------------------------------------------------------------
    buyers = [
        {"buyer_id": "B01", "buyer_name": "Public Works Department (PWD) - Roads Division", "state": "Himachal Pradesh"},
        {"buyer_id": "B02", "buyer_name": "National Highways Authority of India (NHAI) - RO Shimla", "state": "Himachal Pradesh"},
        {"buyer_id": "B03", "buyer_name": "Municipal Corporation Solan - Works Wing", "state": "Himachal Pradesh"},
        {"buyer_id": "B04", "buyer_name": "Rural Development & Panchayati Raj Dept", "state": "Himachal Pradesh"},
        {"buyer_id": "B05", "buyer_name": "State Health Infrastructure Development Agency", "state": "Himachal Pradesh"},
        {"buyer_id": "B06", "buyer_name": "Jal Shakti / State Water & Sewerage Board", "state": "Himachal Pradesh"},
        {"buyer_id": "B07", "buyer_name": "Education Engineering Directorate", "state": "Himachal Pradesh"},
        {"buyer_id": "B08", "buyer_name": "State Electricity Board Ltd (HPSEBL)", "state": "Himachal Pradesh"}
    ]

    sub_categories_map = {
        "Road Infrastructure": ["Rural Road Upgrade", "Highway Widening", "Bridge Construction", "Pavement Overlay"],
        "Civil Construction": ["Community Health Center", "Govt Senior School", "Administrative Complex", "District Sports Stadium"],
        "Water & Sanitation": ["Lift Irrigation Scheme", "Stormwater Drainage Network", "Rural Water Supply Pipeline", "Sewage Treatment Plant"],
        "Electrical & Energy": ["Solar Microgrid 500kW", "Substation 33/11kV", "HT Transmission Line", "Smart Metering System"]
    }

    # -------------------------------------------------------------
    # 4. BENCHMARK CASES DEFINITION (~35 controlled cases)
    # -------------------------------------------------------------
    # Plant specific anomaly combinations across C1–C20
    benchmark_plan = {
        1:  {"scenario": "Single bidder on open tender", "indicators": "C1"},
        2:  {"scenario": "Few bidders with extremely short window", "indicators": "C2,C3"},
        3:  {"scenario": "Excessive technical disqualification", "indicators": "C4"},
        4:  {"scenario": "Lowest bid rejected with narrow margin", "indicators": "C5,C8"},
        5:  {"scenario": "Identical bid prices and close runner-up", "indicators": "C7,C8"},
        6:  {"scenario": "Abnormally low predatory bid", "indicators": "C9"},
        7:  {"scenario": "Abnormally high inflated bid", "indicators": "C9"},
        8:  {"scenario": "Winning bid matches confidential budget", "indicators": "C10"},
        9:  {"scenario": "Abnormal vendor win rate concentration", "indicators": "C11"},
        10: {"scenario": "Award concentration with single buyer", "indicators": "C12,C13"},
        11: {"scenario": "Bid rotation among cartel cluster", "indicators": "C14"},
        12: {"scenario": "Repeated bidder group co-occurrence", "indicators": "C15"},
        13: {"scenario": "Consistent loser cover-bidding pattern", "indicators": "C16"},
        14: {"scenario": "Shared vendor directorship in competing bids", "indicators": "C17"},
        15: {"scenario": "High-value direct contracting risk", "indicators": "C18"},
        16: {"scenario": "Suspected contract splitting below threshold", "indicators": "C19"},
        17: {"scenario": "Unusual weekend midnight publication", "indicators": "C20"},
        18: {"scenario": "Price collusion and shared corporate director", "indicators": "C7,C8,C17"},
        19: {"scenario": "Few bidders, micro bid spread, dominant vendor", "indicators": "C2,C8,C11"},
        20: {"scenario": "Short period, mass disqualification, rejected low bid", "indicators": "C3,C4,C5"},
        21: {"scenario": "High win rate and repeat buyer awards lock-in", "indicators": "C11,C12,C13"},
        22: {"scenario": "Bid rotation with persistent cover bidders", "indicators": "C14,C15,C16"},
        23: {"scenario": "Repeated bidder cohort sharing physical premises", "indicators": "C15,C17"},
        24: {"scenario": "Sole source high-value procurement risk", "indicators": "C1,C18"},
        25: {"scenario": "Price outlier near budget with concentrated vendor", "indicators": "C9,C10,C12"},
        26: {"scenario": "Winning bid submitted seconds before deadline", "indicators": "C6"},
        27: {"scenario": "Suspiciously close bids with shared email domain", "indicators": "C8,C17"},
        28: {"scenario": "Two bidders with winning bid at 99.9% of budget", "indicators": "C2,C10"},
        29: {"scenario": "Mass disqualification leaving dominant contractor", "indicators": "C4,C11"},
        30: {"scenario": "Sequential tender rotation between paired vendors", "indicators": "C13,C14"},
        31: {"scenario": "Lowest bid disqualified in favor of +35% higher bid", "indicators": "C5,C9"},
        32: {"scenario": "Short 4-day window published Saturday midnight", "indicators": "C3,C20"},
        33: {"scenario": "Parent holding company entities winning majority", "indicators": "C12,C17"},
        34: {"scenario": "Cover bidder consistently bidding +5% from same office", "indicators": "C16,C17"},
        35: {"scenario": "Flagship multi-signal collusion cluster", "indicators": "C2,C3,C8,C17"}
    }

    # Add 10 clean control benchmark cases with no expected alerts
    clean_control_indices = [40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
    for idx in clean_control_indices:
        benchmark_plan[idx] = {
            "scenario": "Standard competitive open tender (Clean benchmark control)",
            "indicators": ""
        }

    # -------------------------------------------------------------
    # 5. GENERATE 500 TENDERS, BIDS, AWARDS, CONTRACTS
    # -------------------------------------------------------------
    tenders = []
    bids = []
    awards = []
    contracts = []
    benchmark_cases = []

    bid_counter = 1
    base_date = datetime(2023, 1, 15)

    # Pre-select recurring cartel clusters for rotation and patterns:
    cartel_a = ["V001", "V002", "V003"]  # BuildRight, Apex, Shiva
    cartel_b = ["V006", "V012", "V018"]  # Krishna, Vanguard, Omkar

    for t_idx in range(1, 501):
        t_id = f"T{t_idx:03d}"
        is_benchmark = t_idx in benchmark_plan
        plan = benchmark_plan.get(t_idx, None)
        expected_indicators = plan["indicators"] if plan else ""
        expected_codes = [c.strip() for c in expected_indicators.split(",") if c.strip()]

        # Category & Buyer selection
        cat = categories[(t_idx - 1) % len(categories)]
        sub_cat = random.choice(sub_categories_map[cat])
        buyer = buyers[(t_idx - 1) % len(buyers)]
        loc = cities_states[(t_idx - 1) % len(cities_states)][0]

        # Estimated Value
        if "C18" in expected_codes or t_idx == 15 or t_idx == 24:
            est_val = random.randint(15_00_00_000, 30_00_00_000) # High value for direct award
        elif "C19" in expected_codes or t_idx == 16:
            est_val = 48_50_000 # Just below 50 Lakh threshold
        else:
            est_val = random.randint(35_00_000, 18_00_00_000)

        # Dates
        pub_date = base_date + timedelta(days=t_idx * 1.3)
        if "C20" in expected_codes or t_idx in [17, 32]:
            # Saturday 23:45 publication
            pub_date = pub_date.replace(hour=23, minute=45, second=0)
            days_ahead = 5 - pub_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            pub_date = pub_date + timedelta(days=days_ahead)
        else:
            # Normal tender publication: weekday daylight hours (Mon-Thu 11:30 AM)
            if pub_date.weekday() in [5, 6]:
                pub_date = pub_date + timedelta(days=(7 - pub_date.weekday()))
            pub_date = pub_date.replace(hour=11, minute=30, second=0)

        # Estimated Value & Buyer overrides for specific indicators
        if "C18" in expected_codes or t_idx == 15 or t_idx == 24:
            est_val = random.randint(15_00_00_000, 30_00_00_000) # High value for direct award
        elif "C19" in expected_codes or t_idx == 16:
            est_val = 48_50_000 # Just below 50 Lakh threshold
            buyer = buyers[0] # B01 PWD
            pub_date = datetime(2023, 2, 4, 11, 30, 0)
        elif t_idx in [10, 21, 30]:
            buyer = buyers[0] # Ensure V001 has repeated awards with B01 PWD for C13
            est_val = random.randint(45_00_000, 3_50_00_000)
        elif t_idx == 490:
            # Companion tender for C19 Contract Splitting (same buyer B01 within 2 days, ~48.2 Lakh)
            est_val = 48_20_000
            buyer = buyers[0] # B01 PWD
            pub_date = datetime(2023, 2, 6, 11, 30, 0)
        elif t_idx in clean_control_indices:
            est_val = random.randint(85_00_000, 4_50_00_000)
            pub_date = pub_date.replace(hour=11, minute=30, second=0)
        else:
            est_val = random.randint(35_00_000, 18_00_00_000)

        # Bidding period
        if "C3" in expected_codes or t_idx in [2, 20, 32, 35]:
            sub_window_days = random.randint(3, 6) # Abnormally short
        else:
            sub_window_days = random.randint(21, 35) # Normal

        sub_deadline = pub_date + timedelta(days=sub_window_days, hours=17)
        tech_eval_date = sub_deadline + timedelta(days=random.randint(4, 10))
        fin_eval_date = tech_eval_date + timedelta(days=random.randint(3, 7))
        award_date = fin_eval_date + timedelta(days=random.randint(3, 10))

        # Procurement method
        if "C18" in expected_codes:
            proc_method = "Direct Contracting"
        else:
            proc_method = "Open Competitive Bidding" if random.random() > 0.1 else "Limited Tender"

        t_title = f"{sub_cat} for {buyer['buyer_name'].split('-')[0].strip()} at {loc}"
        if "C19" in expected_codes or t_idx == 16:
            t_title = f"Maintenance & Resurfacing Package B - Sector 4, {loc}"
        elif t_idx == 490:
            t_title = f"Maintenance & Resurfacing Package A - Sector 4, {loc}"

        tenders.append({
            "tender_id": t_id,
            "buyer_id": buyer["buyer_id"],
            "buyer_name": buyer["buyer_name"],
            "tender_title": t_title,
            "category": cat,
            "sub_category": sub_cat,
            "location": loc,
            "state": buyer["state"],
            "estimated_value_inr": est_val,
            "procurement_method": proc_method,
            "award_criteria": "Lowest Evaluated Responsive Bid (L1)",
            "publication_date": pub_date.strftime("%Y-%m-%d %H:%M:%S"),
            "submission_deadline": sub_deadline.strftime("%Y-%m-%d %H:%M:%S"),
            "technical_evaluation_date": tech_eval_date.strftime("%Y-%m-%d"),
            "financial_evaluation_date": fin_eval_date.strftime("%Y-%m-%d"),
            "award_date": award_date.strftime("%Y-%m-%d"),
            "contract_duration_days": random.choice([90, 180, 240, 365, 540]),
            "status": "AWARDED"
        })

        # -------------------------------------------------------------
        # PARTICIPATING VENDORS & BIDS
        # -------------------------------------------------------------
        # Determine number of bidders
        if "C1" in expected_codes or t_idx in [1, 24]:
            num_bidders = 1
        elif "C2" in expected_codes or t_idx in [2, 19, 28, 35]:
            num_bidders = 2
        elif t_idx in clean_control_indices:
            num_bidders = 5
        else:
            num_bidders = random.randint(4, 8)

        # Select participating vendors
        available_vendor_ids = [v["vendor_id"] for v in vendors]

        clean_control_winners = {
            40: "V017", 50: "V021", 60: "V023", 70: "V050", 80: "V034",
            90: "V036", 100: "V038", 110: "V042", 120: "V044", 130: "V048"
        }
        pure_clean_pool = ["V017", "V021", "V023", "V026", "V027", "V029", "V031", "V034", "V035", "V036", "V038", "V039", "V042", "V043", "V044", "V047", "V048", "V049", "V050"]

        if t_idx in clean_control_indices:
            clean_winner = clean_control_winners[t_idx]
            cand_pool = [v for v in pure_clean_pool if v != clean_winner]
            other_4 = random.sample(cand_pool, 4)
            selected_vendors = [clean_winner] + other_4
            winner_vendor = clean_winner
        elif "C14" in expected_codes or "C15" in expected_codes or t_idx in [11, 12, 13, 22, 23]:
            selected_vendors = list(cartel_a)
            while len(selected_vendors) < num_bidders:
                cand = random.choice(available_vendor_ids)
                if cand not in selected_vendors:
                    selected_vendors.append(cand)
        elif "C17" in expected_codes or t_idx in [14, 18, 27, 34]:
            selected_vendors = ["V001", "V002"] # Shared director & address
            while len(selected_vendors) < num_bidders:
                cand = random.choice(available_vendor_ids)
                if cand not in selected_vendors:
                    selected_vendors.append(cand)
        elif "C11" in expected_codes or t_idx in [9, 10, 19, 21, 29]:
            selected_vendors = ["V001"]
            while len(selected_vendors) < num_bidders:
                cand = random.choice(available_vendor_ids)
                if cand not in selected_vendors:
                    selected_vendors.append(cand)
        else:
            selected_vendors = random.sample(available_vendor_ids, num_bidders)

        # Determine winner
        if t_idx in clean_control_indices:
            winner_vendor = clean_control_winners[t_idx]
        elif "C14" in expected_codes or t_idx in [11, 22, 30]:
            winner_vendor = cartel_a[(t_idx % len(cartel_a))]
            if winner_vendor not in selected_vendors:
                selected_vendors.append(winner_vendor)
        elif "C16" in expected_codes or t_idx in [13, 34]:
            winner_vendor = "V001"
            if winner_vendor not in selected_vendors:
                selected_vendors.append(winner_vendor)
        elif "C11" in expected_codes or "C12" in expected_codes or t_idx in [9, 10, 19, 21] or (t_idx % 18 == 0 and t_idx not in clean_control_indices):
            winner_vendor = "V001"
            if winner_vendor not in selected_vendors:
                selected_vendors.append(winner_vendor)
        elif "C18" in expected_codes and t_idx in [15, 24]:
            winner_vendor = selected_vendors[0]
        else:
            winner_vendor = random.choice(selected_vendors)

        # Calculate Bids for each participating vendor
        tender_bids = []
        for v_idx, v_id in enumerate(selected_vendors):
            is_w = (v_id == winner_vendor)

            # Bid amount logic
            if t_idx in clean_control_indices:
                if is_w:
                    bid_amt = round(est_val * 0.915)
                    bid_status = "QUALIFIED"
                    tech_score = 92.0
                    fin_score = 94.0
                    dq_reason = None
                else:
                    bid_amt = round(est_val * (0.965 + v_idx * 0.035))
                    bid_status = "QUALIFIED"
                    tech_score = round(85.0 + v_idx * 1.5, 1)
                    fin_score = round(80.0 + v_idx * 2.0, 1)
                    dq_reason = None
            elif is_w:
                if "C9" in expected_codes and t_idx in [6]:
                    bid_amt = round(est_val * 0.58)
                elif "C9" in expected_codes and t_idx in [7, 31]:
                    bid_amt = round(est_val * 1.44)
                elif "C10" in expected_codes or t_idx in [8, 25, 28]:
                    bid_amt = round(est_val * 0.9992)
                else:
                    bid_amt = round(est_val * (0.88 + random.uniform(0.01, 0.09)))
            else:
                if "C9" in expected_codes and t_idx == 25 and v_idx == 1:
                    bid_amt = round(est_val * 1.42)
                elif "C7" in expected_codes and t_idx in [5, 18]:
                    bid_amt = round(est_val * 0.94)
                elif "C8" in expected_codes or t_idx in [4, 5, 18, 19, 27, 35]:
                    bid_amt = round(est_val * 0.95)
                elif "C16" in expected_codes and v_id in ["V002", "V006"]:
                    bid_amt = round(est_val * 1.05)
                else:
                    bid_amt = round(est_val * (0.92 + random.uniform(0.02, 0.22)))

            # Submission timestamp
            if "C6" in expected_codes and is_w and t_idx == 26:
                bid_time = sub_deadline - timedelta(seconds=42)
            else:
                bid_time = sub_deadline - timedelta(days=random.randint(1, max(1, sub_window_days - 1)), hours=random.randint(1, 8))

            # Disqualification logic (skip for clean control)
            if t_idx not in clean_control_indices:
                if "C4" in expected_codes and not is_w:
                    bid_status = "DISQUALIFIED"
                    dq_reason = random.choice([
                        "Technical criteria deficit: past similar experience below threshold",
                        "Defective EMD bank guarantee instrument",
                        "Non-submission of audited turnover sheet for FY23"
                    ])
                    tech_score = round(random.uniform(42.0, 58.0), 1)
                elif "C5" in expected_codes and v_idx == 1 and not is_w:
                    bid_status = "DISQUALIFIED"
                    dq_reason = "Minor technical non-compliance in machinery deployment schedule"
                    tech_score = 68.0
                else:
                    if not is_w and random.random() < 0.12 and "C4" not in expected_codes:
                        bid_status = "DISQUALIFIED"
                        dq_reason = "Technical evaluation: non-compliant asphalt batching plant certification"
                        tech_score = round(random.uniform(50.0, 64.0), 1)
                    else:
                        bid_status = "QUALIFIED"
                        dq_reason = None
                        tech_score = round(random.uniform(75.0, 96.0), 1)
                fin_score = round(random.uniform(70.0, 95.0), 1) if bid_status == "QUALIFIED" else 0.0

            b_id = f"B{bid_counter:04d}"
            bid_counter += 1

            tender_bids.append({
                "bid_id": b_id,
                "tender_id": t_id,
                "vendor_id": v_id,
                "bid_amount_inr": bid_amt,
                "submission_timestamp": bid_time.strftime("%Y-%m-%d %H:%M:%S"),
                "bid_status": bid_status,
                "disqualification_reason": dq_reason if dq_reason else "",
                "technical_score": tech_score,
                "financial_score": fin_score,
                "is_winner": is_w
            })

        # Post-adjust bids for specific indicators (C5, C7, C8)
        winner_bid_obj = next(b for b in tender_bids if b["is_winner"])

        if "C7" in expected_codes:
            other_qualified = [b for b in tender_bids if not b["is_winner"] and b["bid_status"] == "QUALIFIED"]
            if other_qualified:
                other_qualified[0]["bid_amount_inr"] = winner_bid_obj["bid_amount_inr"]

        if "C8" in expected_codes:
            # Runner-up bid within 0.15% spread
            other_qual = [b for b in tender_bids if not b["is_winner"] and b["bid_status"] == "QUALIFIED"]
            if other_qual:
                other_qual[0]["bid_amount_inr"] = round(winner_bid_obj["bid_amount_inr"] * 1.0015)
            else:
                other_bids = [b for b in tender_bids if not b["is_winner"]]
                if other_bids:
                    other_bids[0]["bid_amount_inr"] = round(winner_bid_obj["bid_amount_inr"] * 1.0015)

        if "C5" in expected_codes:
            # Ensure rejected lower bid exists
            dq_bids = [b for b in tender_bids if b["bid_status"] == "DISQUALIFIED"]
            if dq_bids:
                dq_bids[0]["bid_amount_inr"] = round(winner_bid_obj["bid_amount_inr"] * 0.94)

        # Append bids
        for b in tender_bids:
            bids.append(b)

        # -------------------------------------------------------------
        # AWARDS (1 per tender)
        # -------------------------------------------------------------
        a_id = f"A{t_idx:03d}"
        winning_amt = winner_bid_obj["bid_amount_inr"]
        awards.append({
            "award_id": a_id,
            "tender_id": t_id,
            "winner_vendor_id": winner_vendor,
            "awarded_amount_inr": winning_amt,
            "award_date": award_date.strftime("%Y-%m-%d"),
            "award_reason": "Lowest responsive and technically qualified bidder (L1)"
        })

        # -------------------------------------------------------------
        # CONTRACTS (1 per tender)
        # -------------------------------------------------------------
        c_id = f"C{t_idx:03d}"
        start_date = award_date + timedelta(days=14)
        planned_dur = tenders[-1]["contract_duration_days"]
        planned_end = start_date + timedelta(days=planned_dur)

        # Add delay for some cases
        if t_idx in [1, 2, 9, 35] or random.random() < 0.25:
            delay_days = random.randint(30, 120)
            actual_end = planned_end + timedelta(days=delay_days)
            actual_dur = planned_dur + delay_days
            status = "DELAYED" if delay_days > 60 else "COMPLETED"
        else:
            actual_end = planned_end
            actual_dur = planned_dur
            status = "COMPLETED"

        contracts.append({
            "contract_id": c_id,
            "tender_id": t_id,
            "vendor_id": winner_vendor,
            "contract_value_inr": winning_amt,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "planned_end_date": planned_end.strftime("%Y-%m-%d"),
            "actual_end_date": actual_end.strftime("%Y-%m-%d"),
            "planned_duration_days": planned_dur,
            "actual_duration_days": actual_dur,
            "completion_status": status
        })

        # -------------------------------------------------------------
        # BENCHMARK CASE RECORD
        # -------------------------------------------------------------
        if is_benchmark:
            benchmark_cases.append({
                "tender_id": t_id,
                "expected_indicator_codes": expected_indicators,
                "scenario_type": plan["scenario"],
                "benchmark_alert": True if expected_indicators != "" else False
            })

    # -------------------------------------------------------------
    # 6. DERIVE TOGETHER PARTICIPATION (strictly from bids)
    # -------------------------------------------------------------
    # Build a map of tender -> set of vendor_ids
    tender_vendors_map = {}
    vendor_tender_counts = {v["vendor_id"]: 0 for v in vendors}

    for b in bids:
        t_id = b["tender_id"]
        v_id = b["vendor_id"]
        if t_id not in tender_vendors_map:
            tender_vendors_map[t_id] = set()
        tender_vendors_map[t_id].add(v_id)
        vendor_tender_counts[v_id] += 1

    pair_counts = {}
    for t_id, v_set in tender_vendors_map.items():
        v_list = sorted(list(v_set))
        for i in range(len(v_list)):
            for j in range(i + 1, len(v_list)):
                pair = (v_list[i], v_list[j])
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

    together_participation = []
    for (v1, v2), count in sorted(pair_counts.items(), key=lambda x: -x[1]):
        # Calculate together_percentage as ratio over min participation of the two
        min_participations = min(vendor_tender_counts[v1], vendor_tender_counts[v2])
        pct = round((count / max(1, min_participations)) * 100.0, 1)
        together_participation.append({
            "vendor_1": v1,
            "vendor_2": v2,
            "together_tender_count": count,
            "together_percentage": pct
        })

    # -------------------------------------------------------------
    # 7. WRITE TO CSV FILES
    # -------------------------------------------------------------
    def write_csv(filename, fieldnames, data):
        path = os.path.join(output_dir, filename)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"✓ Wrote {len(data):>5} rows to {path}")

    write_csv("vendors.csv", list(vendors[0].keys()), vendors)
    write_csv("tenders.csv", list(tenders[0].keys()), tenders)
    write_csv("bids.csv", list(bids[0].keys()), bids)
    write_csv("awards.csv", list(awards[0].keys()), awards)
    write_csv("contracts.csv", list(contracts[0].keys()), contracts)
    write_csv("vendor_relationships.csv", list(relationships[0].keys()), relationships)
    write_csv("together_participation.csv", list(together_participation[0].keys()), together_participation)
    write_csv("benchmark_cases.csv", list(benchmark_cases[0].keys()), benchmark_cases)

    print("\nDataset Generation Complete!")
    print(f"Total Vendors: {len(vendors)}")
    print(f"Total Tenders: {len(tenders)}")
    print(f"Total Bids: {len(bids)}")
    print(f"Total Awards: {len(awards)}")
    print(f"Total Contracts: {len(contracts)}")
    print(f"Total Relationships: {len(relationships)}")
    print(f"Total Together Participation Pairs: {len(together_participation)}")
    print(f"Total Benchmark Cases: {len(benchmark_cases)} (Anomalous: {sum(1 for b in benchmark_cases if b['benchmark_alert'])}, Clean Controls: {sum(1 for b in benchmark_cases if not b['benchmark_alert'])})")

if __name__ == "__main__":
    generate_dataset()
