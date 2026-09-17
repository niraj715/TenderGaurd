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

def test_c1_single_bidder():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T001")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C1" in codes, "C1 (Single Bidder) should be detected for T001"

def test_c2_abnormally_few_bidders():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T002")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C2" in codes, "C2 (Few Bidders) should be detected for T002"

def test_c3_short_bidding_period():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T002")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C3" in codes, "C3 (Short Bidding Period) should be detected for T002"

def test_c4_excessive_disqualification():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T003")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C4" in codes, "C4 (Excessive Disqualification) should be detected for T003"

def test_c5_lowest_bid_rejected():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T004")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C5" in codes, "C5 (Lowest Bid Rejected) should be detected for T004"

def test_c6_late_winning_bid():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T026")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C6" in codes, "C6 (Late Winning Bid) should be detected for T026"
