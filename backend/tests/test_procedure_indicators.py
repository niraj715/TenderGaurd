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

def test_c18_direct_limited_award_risk():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T015")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C18" in codes, "C18 (Direct Award Risk) should be detected for T015"

def test_c19_contract_splitting():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T016")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C19" in codes, "C19 (Contract Splitting) should be detected for T016"

def test_c20_unusual_timing():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T017")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C20" in codes, "C20 (Unusual Timing) should be detected for T017"
