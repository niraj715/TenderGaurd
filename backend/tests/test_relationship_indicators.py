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

def test_c17_shared_vendor_information():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T014")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C17" in codes, "C17 (Shared Vendor Information) should be detected for T014"
