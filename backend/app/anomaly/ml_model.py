import numpy as np
from typing import List, Dict, Any
from sklearn.ensemble import IsolationForest

class ProcurementIsolationForest:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.15, random_state=42)
        self.is_fitted = False

    def fit_and_score(self, features: List[List[float]]) -> List[float]:
        """
        Features per case:
        [
            bid_amount_norm,
            pricing_deviation_pct,
            vendor_win_rate,
            delay_pct,
            maintenance_ratio,
            complaint_count
        ]
        """
        if len(features) < 4:
            # Fallback heuristic if dataset is very small
            scores = []
            for f in features:
                # weighted sum of normalized deviations
                heuristic = (f[1]/50.0)*0.25 + f[2]*0.25 + (f[3]/100.0)*0.20 + (f[4]/3.0)*0.15 + (f[5]/20.0)*0.15
                scores.append(min(1.0, max(0.0, heuristic)))
            return scores
        
        X = np.array(features, dtype=float)
        self.model.fit(X)
        self.is_fitted = True
        
        # decision_function returns negative values for anomalies, positive for normal
        raw_scores = self.model.decision_function(X)
        # normalize to 0..1 where 1 is highest anomaly
        min_s = float(np.min(raw_scores))
        max_s = float(np.max(raw_scores))
        span = max_s - min_s if max_s != min_s else 1.0
        
        anomaly_scores = [float(1.0 - ((s - min_s) / span)) for s in raw_scores]
        return anomaly_scores

ml_detector = ProcurementIsolationForest()
