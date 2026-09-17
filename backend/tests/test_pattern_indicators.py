import csv
import pytest
from backend.app.anomaly.c_indicators import AnomalyIndicatorEngine

def load_data():
    def load(fn):
        with open("data/generated/" + fn, mode="r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    return (
        load("tenders.csv"), load("bids.csv"), load("awards.csv"),
        load("vendors.csv"), load("vendor_relationships.csv"), load("together_participation.csv")
    )

def test_c14_bid_rotation():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T011")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C14" in codes, "C14 (Bid Rotation) should be detected for T011"

def test_c15_repeated_bidder_groups():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T012")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C15" in codes, "C15 (Repeated Groups) should be detected for T012"

def test_c16_consistent_loser_winner_patterns():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T013")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C16" in codes, "C16 (Consistent Loser) should be detected for T013"
