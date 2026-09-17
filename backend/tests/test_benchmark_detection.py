import pytest
from scripts.evaluate_benchmark import run_evaluation

def test_synthetic_benchmark_evaluation():
    metrics = run_evaluation()
    assert metrics["precision"] >= 0.90, f"Precision {metrics['precision']} < 0.90"
    assert metrics["recall"] >= 0.90, f"Recall {metrics['recall']} < 0.90"
    assert metrics["f1"] >= 0.90, f"F1-Score {metrics['f1']} < 0.90"
    assert metrics["fpr"] <= 0.10, f"False Positive Rate {metrics['fpr']} > 0.10"
