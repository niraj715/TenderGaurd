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

def test_c11_abnormal_vendor_win_rate():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T009")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C11" in codes, "C11 (Abnormal Vendor Win Rate) should be detected for T009"

def test_c12_award_concentration():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T010")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C12" in codes, "C12 (Award Concentration) should be detected for T010"

def test_c13_repeated_buyer_vendor_awards():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T010")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C13" in codes, "C13 (Repeated Buyer Awards) should be detected for T010"
