"""
ProcureShield AI — Synthetic Benchmark Evaluation Script
Evaluates C1–C20 detection engine against synthetic ground truth benchmark cases.
Computes Precision, Recall, F1 Score, False Positive Rate, and Confusion Matrix.
"""

import os
import csv
from backend.app.anomaly.c_indicators import AnomalyIndicatorEngine

def load_csv(data_dir, filename):
    path = os.path.join(data_dir, filename)
    with open(path, mode="r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def run_evaluation(data_dir: str = "data/generated"):
    tenders = load_csv(data_dir, "tenders.csv")
    bids = load_csv(data_dir, "bids.csv")
    awards = load_csv(data_dir, "awards.csv")
    vendors = load_csv(data_dir, "vendors.csv")
    relationships = load_csv(data_dir, "vendor_relationships.csv")
    together = load_csv(data_dir, "together_participation.csv")
    benchmarks = load_csv(data_dir, "benchmark_cases.csv")

    benchmark_map = {b["tender_id"]: b for b in benchmarks}

    engine = AnomalyIndicatorEngine(tenders, bids, awards, vendors, relationships, together)

    print("Running detection engine on 500 tenders...")
    results = {}
    for t in tenders:
        t_id = t["tender_id"]
        res = engine.evaluate_tender(t_id)
        results[t_id] = res

    # Evaluation against benchmark cases
    # A tender is considered an "Alert" by the engine if priority_score >= 50.0 or len(signals) >= 1
    tp = 0
    fp = 0
    fn = 0
    tn = 0

    indicator_tp = {f"C{i}": 0 for i in range(1, 21)}
    indicator_expected = {f"C{i}": 0 for i in range(1, 21)}

    for t_id, bm in benchmark_map.items():
        is_true_anomaly = bm["benchmark_alert"] in ["True", "true", True]
        res = results[t_id]
        detected_codes = {ind["indicator_code"] for ind in res["detected_indicators"]}
        expected_codes = {c.strip() for c in bm["expected_indicator_codes"].split(",") if c.strip()}

        for code in expected_codes:
            if code in indicator_expected:
                indicator_expected[code] += 1
                if code in detected_codes:
                    indicator_tp[code] += 1

        engine_alert = res["priority_score"] >= 50.0 or len(res["detected_indicators"]) > 0

        if is_true_anomaly and engine_alert:
            tp += 1
        elif not is_true_anomaly and engine_alert:
            fp += 1
        elif is_true_anomaly and not engine_alert:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    print("\n" + "=" * 65)
    print("      PROCURESHIELD AI — SYNTHETIC BENCHMARK EVALUATION")
    print("=" * 65)
    print(f"Total Benchmark Cases Evaluated: {len(benchmark_map)}")
    print(f"  • Ground Truth Anomalies:      {tp + fn}")
    print(f"  • Ground Truth Clean Controls: {fp + tn}")
    print("-" * 65)
    print("CONFUSION MATRIX:")
    print(f"  True Positives  (TP): {tp:>3}    |  False Positives (FP): {fp:>3}")
    print(f"  False Negatives (FN): {fn:>3}    |  True Negatives  (TN): {tn:>3}")
    print("-" * 65)
    print("PERFORMANCE METRICS:")
    print(f"  Precision:           {precision * 100:.2f}%")
    print(f"  Recall:              {recall * 100:.2f}%")
    print(f"  F1-Score:            {f1 * 100:.2f}%")
    print(f"  False Positive Rate: {fpr * 100:.2f}%")
    print("=" * 65)

    print("\nINDICATOR DETECTION BREAKDOWN (C1–C20):")
    print("Code | Indicator Name                   | Planted | Detected | Recall")
    print("-" * 65)
    code_names = {
        "C1": "Single Bidder", "C2": "Few Bidders", "C3": "Short Bidding Period",
        "C4": "Excessive Disqualification", "C5": "Lowest Bid Rejected", "C6": "Late Winning Bid",
        "C7": "Identical Bid Prices", "C8": "Suspiciously Close Bids", "C9": "Abnormally Low/High",
        "C10": "Close to Budget", "C11": "Abnormal Win Rate", "C12": "Award Concentration",
        "C13": "Repeated Awards", "C14": "Bid Rotation", "C15": "Repeated Groups",
        "C16": "Consistent Loser", "C17": "Shared Vendor Info", "C18": "Direct Award Risk",
        "C19": "Contract Splitting", "C20": "Unusual Timing"
    }

    for i in range(1, 21):
        code = f"C{i}"
        exp = indicator_expected[code]
        det = indicator_tp[code]
        rec = (det / exp * 100) if exp > 0 else 100.0
        print(f"{code:<4} | {code_names.get(code, ''):<32} | {exp:>7} | {det:>8} | {rec:>5.1f}%")

    print("=" * 65)
    print("NOTE: This is a synthetic benchmark evaluation over controlled planted cases.")
    print("These metrics evaluate algorithmic rediscovery, not real-world fraud conviction.\n")

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": precision, "recall": recall, "f1": f1, "fpr": fpr,
        "indicator_tp": indicator_tp, "indicator_expected": indicator_expected
    }

if __name__ == "__main__":
    run_evaluation()
