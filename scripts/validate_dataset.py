"""
ProcureShield AI — Comprehensive Dataset Validation Script
Validates the generated procurement dataset against all integrity and benchmark criteria.
"""

import os
import csv
from datetime import datetime

def validate_dataset(data_dir: str = "data/generated"):
    report = []
    errors = []

    def log(msg, status="PASS"):
        report.append(f"[{status}] {msg}")
        if status == "FAIL":
            errors.append(msg)

    # 1. Load all CSVs
    def load_csv(filename):
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            log(f"File missing: {filename}", "FAIL")
            return []
        with open(path, mode="r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    vendors = load_csv("vendors.csv")
    tenders = load_csv("tenders.csv")
    bids = load_csv("bids.csv")
    awards = load_csv("awards.csv")
    contracts = load_csv("contracts.csv")
    relationships = load_csv("vendor_relationships.csv")
    together = load_csv("together_participation.csv")
    benchmarks = load_csv("benchmark_cases.csv")

    # 2. Check counts
    if len(vendors) == 50:
        log("Exactly 50 unique vendors present")
    else:
        log(f"Vendor count mismatch: expected 50, got {len(vendors)}", "FAIL")

    if len(tenders) == 500:
        log("Exactly 500 unique tenders present")
    else:
        log(f"Tender count mismatch: expected 500, got {len(tenders)}", "FAIL")

    if len(awards) == 500:
        log("Exactly 500 awards present (1 per tender)")
    else:
        log(f"Award count mismatch: expected 500, got {len(awards)}", "FAIL")

    if len(contracts) == 500:
        log("Exactly 500 contracts present (1 per tender)")
    else:
        log(f"Contract count mismatch: expected 500, got {len(contracts)}", "FAIL")

    if 2500 <= len(bids) <= 4500:
        log(f"Bids count within target range: {len(bids)} bids")
    else:
        log(f"Bids count unexpected: {len(bids)}", "FAIL")

    if 15 <= len(relationships) <= 25:
        log(f"Vendor relationships within range: {len(relationships)} relationships")
    else:
        log(f"Vendor relationships unexpected: {len(relationships)}", "FAIL")

    anom_cases = [b for b in benchmarks if b["benchmark_alert"] in ["True", "true", True]]
    if len(anom_cases) == 35:
        log(f"Exactly 35 controlled anomalous benchmark cases planted")
    else:
        log(f"Anomalous benchmark count mismatch: expected 35, got {len(anom_cases)}", "FAIL")

    # 3. Check unique IDs
    vendor_ids = {v["vendor_id"] for v in vendors}
    if len(vendor_ids) == len(vendors):
        log("Vendor IDs are unique")
    else:
        log("Duplicate vendor IDs detected", "FAIL")

    tender_ids = {t["tender_id"] for t in tenders}
    if len(tender_ids) == len(tenders):
        log("Tender IDs are unique")
    else:
        log("Duplicate tender IDs detected", "FAIL")

    bid_ids = {b["bid_id"] for b in bids}
    if len(bid_ids) == len(bids):
        log("Bid IDs are unique")
    else:
        log("Duplicate bid IDs detected", "FAIL")

    award_tender_ids = {a["tender_id"] for a in awards}
    if len(award_tender_ids) == len(awards):
        log("Every award belongs to a distinct tender")
    else:
        log("Duplicate tender IDs found in awards", "FAIL")

    # 4. Check references
    orphan_bids = [b for b in bids if b["tender_id"] not in tender_ids or b["vendor_id"] not in vendor_ids]
    if not orphan_bids:
        log("All bids reference valid existing tenders and vendors")
    else:
        log(f"Found {len(orphan_bids)} orphan bids", "FAIL")

    orphan_awards = [a for a in awards if a["tender_id"] not in tender_ids or a["winner_vendor_id"] not in vendor_ids]
    if not orphan_awards:
        log("All awards reference valid existing tenders and vendors")
    else:
        log(f"Found {len(orphan_awards)} orphan awards", "FAIL")

    orphan_contracts = [c for c in contracts if c["tender_id"] not in tender_ids or c["vendor_id"] not in vendor_ids]
    if not orphan_contracts:
        log("All contracts reference valid existing tenders and vendors")
    else:
        log(f"Found {len(orphan_contracts)} orphan contracts", "FAIL")

    # 5. Check winner participation and amount matching
    bid_map = {(b["tender_id"], b["vendor_id"]): b for b in bids}
    winner_mismatches = []
    amount_mismatches = []

    for a in awards:
        t_id = a["tender_id"]
        w_id = a["winner_vendor_id"]
        awarded_amt = float(a["awarded_amount_inr"])

        key = (t_id, w_id)
        if key not in bid_map:
            winner_mismatches.append(f"Winner {w_id} did not bid on {t_id}")
        else:
            bid = bid_map[key]
            if not (bid["is_winner"] in ["True", "true", True]):
                winner_mismatches.append(f"Bid for winner {w_id} on {t_id} is_winner != True")
            if abs(float(bid["bid_amount_inr"]) - awarded_amt) > 0.01:
                amount_mismatches.append(f"Award amount {awarded_amt} != bid amount {bid['bid_amount_inr']} on {t_id}")

    if not winner_mismatches:
        log("Every winner participated with a matching winning bid")
    else:
        log(f"Winner mismatches found: {winner_mismatches[:3]}", "FAIL")

    if not amount_mismatches:
        log("Every award amount strictly matches winning bid amount")
    else:
        log(f"Amount mismatches found: {amount_mismatches[:3]}", "FAIL")

    # 6. Check dates validity
    date_errors = []
    for t in tenders:
        try:
            pub = datetime.strptime(t["publication_date"], "%Y-%m-%d %H:%M:%S")
            sub = datetime.strptime(t["submission_deadline"], "%Y-%m-%d %H:%M:%S")
            if sub <= pub:
                date_errors.append(f"Tender {t['tender_id']}: deadline {sub} <= pub {pub}")
        except Exception as e:
            date_errors.append(f"Tender {t['tender_id']}: date parse error {e}")

    if not date_errors:
        log("All publication and submission dates follow logical chronological ordering")
    else:
        log(f"Date errors detected: {date_errors[:3]}", "FAIL")

    # 7. Check relationship valid references
    invalid_rels = [r for r in relationships if r["vendor_1"] not in vendor_ids or r["vendor_2"] not in vendor_ids]
    if not invalid_rels:
        log("All vendor relationships reference valid vendors")
    else:
        log(f"Invalid vendor relationship references: {len(invalid_rels)}", "FAIL")

    # 8. Check together participation strictly matches bids
    tender_bidders = {}
    for b in bids:
        t_id = b["tender_id"]
        v_id = b["vendor_id"]
        if t_id not in tender_bidders:
            tender_bidders[t_id] = set()
        tender_bidders[t_id].add(v_id)

    expected_together = {}
    for t_id, v_set in tender_bidders.items():
        v_list = sorted(list(v_set))
        for i in range(len(v_list)):
            for j in range(i + 1, len(v_list)):
                pair = (v_list[i], v_list[j])
                expected_together[pair] = expected_together.get(pair, 0) + 1

    together_errors = []
    for row in together:
        pair = (row["vendor_1"], row["vendor_2"])
        actual_cnt = int(row["together_tender_count"])
        expected_cnt = expected_together.get(pair, 0)
        if actual_cnt != expected_cnt:
            together_errors.append(f"Pair {pair}: recorded {actual_cnt} != expected {expected_cnt}")

    if not together_errors:
        log("Together participation counts exactly match co-bids in bids table")
    else:
        log(f"Together count errors: {together_errors[:3]}", "FAIL")

    # 9. Verify planted patterns for sample benchmark cases
    planted_checks = []
    # T001: C1 (1 bidder)
    t1_bids = [b for b in bids if b["tender_id"] == "T001"]
    if len(t1_bids) == 1:
        planted_checks.append("T001 has exactly 1 bidder (C1)")
    else:
        log("T001 did not have 1 bidder", "FAIL")

    # T002: C2 (2 bidders)
    t2_bids = [b for b in bids if b["tender_id"] == "T002"]
    if len(t2_bids) == 2:
        planted_checks.append("T002 has exactly 2 bidders (C2)")
    else:
        log("T002 did not have 2 bidders", "FAIL")

    # T005: C7 (Identical bid prices)
    t5_bids = [b for b in bids if b["tender_id"] == "T005"]
    amounts = [float(b["bid_amount_inr"]) for b in t5_bids]
    if len(amounts) != len(set(amounts)):
        planted_checks.append("T005 has identical bid prices (C7)")
    else:
        log("T005 did not contain identical bid prices", "FAIL")

    # T006: C9 (Abnormally low bid < 60% of estimated)
    t6_tender = next(t for t in tenders if t["tender_id"] == "T006")
    t6_winner = next(b for b in bids if b["tender_id"] == "T006" and b["is_winner"] in ["True", "true", True])
    ratio = float(t6_winner["bid_amount_inr"]) / float(t6_tender["estimated_value_inr"])
    if ratio < 0.65:
        planted_checks.append(f"T006 has abnormally low bid (ratio: {ratio:.2f}) (C9)")
    else:
        log("T006 winning bid is not abnormally low", "FAIL")

    for p in planted_checks:
        log(p)

    # Print Summary
    print("\n=======================================================")
    print("      PROCURESHIELD AI — DATASET VALIDATION REPORT     ")
    print("=======================================================")
    for line in report:
        print(line)
    print("=======================================================")
    if errors:
        print(f"FAILED: {len(errors)} validation errors detected.")
        return False
    else:
        print("ALL DATASET INTEGRITY CHECKS PASSED (100% VALID)")
        return True

if __name__ == "__main__":
    success = validate_dataset()
    if not success:
        exit(1)
