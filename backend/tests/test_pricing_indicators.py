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

def test_c7_identical_bid_prices():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T005")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C7" in codes, "C7 (Identical Bid Prices) should be detected for T005"

def test_c8_suspiciously_close_bids():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T004")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C8" in codes, "C8 (Suspiciously Close Bids) should be detected for T004"

def test_c9_abnormally_low_bid():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T006")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C9" in codes, "C9 (Abnormally Low Bid) should be detected for T006"

def test_c9_abnormally_high_bid():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T007")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C9" in codes, "C9 (Abnormally High Bid) should be detected for T007"

def test_c10_bid_unusually_close_to_budget():
    engine = AnomalyIndicatorEngine(*load_data())
    res = engine.evaluate_tender("T008")
    codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
    assert "C10" in codes, "C10 (Close to Budget) should be detected for T008"
