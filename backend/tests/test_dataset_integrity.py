import os
import csv
import pytest

DATA_DIR = "data/generated"

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    assert os.path.exists(path), f"File {filename} does not exist"
    with open(path, mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def test_entity_counts():
    vendors = load_csv("vendors.csv")
    tenders = load_csv("tenders.csv")
    bids = load_csv("bids.csv")
    awards = load_csv("awards.csv")
    contracts = load_csv("contracts.csv")
    relationships = load_csv("vendor_relationships.csv")
    together = load_csv("together_participation.csv")
    benchmarks = load_csv("benchmark_cases.csv")

    assert len(vendors) == 50, f"Expected 50 vendors, got {len(vendors)}"
    assert len(tenders) == 500, f"Expected 500 tenders, got {len(tenders)}"
    assert len(awards) == 500, f"Expected 500 awards, got {len(awards)}"
    assert len(contracts) == 500, f"Expected 500 contracts, got {len(contracts)}"
    assert 2500 <= len(bids) <= 4000, f"Expected bids in 2500-4000, got {len(bids)}"
    assert 15 <= len(relationships) <= 25, f"Expected 15-25 relationships, got {len(relationships)}"
    assert len(together) > 500, f"Expected together participation pairs, got {len(together)}"
    assert len(benchmarks) >= 35, f"Expected >= 35 benchmarks, got {len(benchmarks)}"

def test_referential_integrity():
    vendors = {v["vendor_id"] for v in load_csv("vendors.csv")}
    tenders = {t["tender_id"] for t in load_csv("tenders.csv")}
    bids = load_csv("bids.csv")
    awards = load_csv("awards.csv")
    contracts = load_csv("contracts.csv")

    # Every bid references valid tender and vendor
    for b in bids:
        assert b["tender_id"] in tenders, f"Invalid tender_id in bid {b['bid_id']}"
        assert b["vendor_id"] in vendors, f"Invalid vendor_id in bid {b['bid_id']}"

    # Every award matches winning bid
    bids_map = {(b["tender_id"], b["vendor_id"]): b for b in bids}
    for a in awards:
        assert a["tender_id"] in tenders
        assert a["winner_vendor_id"] in vendors
        key = (a["tender_id"], a["winner_vendor_id"])
        assert key in bids_map, f"Winner {a['winner_vendor_id']} did not bid in {a['tender_id']}"
        b = bids_map[key]
        assert float(a["awarded_amount_inr"]) == float(b["bid_amount_inr"]), "Award amount mismatch"

    # Every contract matches tender
    for c in contracts:
        assert c["tender_id"] in tenders
        assert c["vendor_id"] in vendors
